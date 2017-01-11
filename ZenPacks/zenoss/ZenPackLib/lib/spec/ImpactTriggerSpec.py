##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .Spec import Spec


class ImpactTriggerSpec(Spec):
    """Initialize an Impact Trigger"""
    _policy = None
    _trigger = None
    _threshold = None
    _state = None
    _dependent_state = None

    _policy_types = ['AVAILABILITY', 'PERFORMANCE', 'CAPACITY']
    _avail_states = ['DOWN', 'UP', 'DEGRADED', 'ATRISK', 'UNKNOWN']
    _perf_states = ['UNACCEPTABLE', 'DEGRADED', 'ACCEPTABLE', 'UNKNOWN']
    _cap_states = ['UNACCEPTABLE', 'REDUCED', 'ACCEPTABLE', 'UNKNOWN']
    _trigger_types = ['policyPercentageTrigger', 'policyThresholdTrigger', 'negativeThresholdTrigger']

    def __init__(
            self,
            class_spec,
            name,
            policy='Availability',
            trigger='policyPercentageTrigger',
            threshold=50,
            state='DOWN',
            dependent_state='DOWN',
            _source_location=None,
            zplog=None):
        """
        Create an Impact Trigger Specification

            :param policy: One of: AVAILABILITY, PERFORMANCE, CAPACITY
            :type policy: str
            :param trigger: One of impact policyPercentageTrigger, policyThresholdTrigger, or negativeThresholdTrigger
            :type trigger: str
            :param threshold: threshold should be an integer
            :type threshold: int
            :param state: State
            :type state: str
            :param dependent_state: Dependent State
            :type dependent_state: str
        """
        super(ImpactTriggerSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog
        self.class_spec = class_spec
        self.name = name
        self.policy = policy
        self.trigger = trigger
        self.threshold = threshold
        self.state = state
        self.dependent_state = dependent_state

    @property
    def policy(self):
        return self._policy

    @policy.setter
    def policy(self, value):
        if value.upper() in self._policy_types:
            self._policy = value.upper()
        else:
            self._policy = 'AVAILABILITY'
            self.LOG.warn('Impact Trigger policy should be one of {} (using {}).'.format(self._policy_types, self._policy))

    @property
    def trigger(self):
        return self._trigger

    @trigger.setter
    def trigger(self, value):
        if value in self._trigger_types:
            self._trigger = value
        else:
            self._trigger = 'policyPercentageTrigger'
            self.LOG.warn('Impact Trigger trigger should be one of {} (using {}).'.format(self._trigger_types, self._trigger))

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        value = int(value)
        # if this is a percentage trigger, ensure the value lies between 0 and 100
        if self.trigger == 'policyPercentageTrigger':
            self._threshold = max(0, min(100, value))
        else:
            self._threshold = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value.upper() in self.valid_states:
            self._state = value.upper()
        else:
            self._state = 'UNKNOWN'
            self.LOG.warn('Impact Trigger state should be one of {} (using {}).'.format(self.valid_states, self._state))

    @property
    def dependent_state(self):
        return self._dependent_state

    @dependent_state.setter
    def dependent_state(self, value):
        if value.upper() in self.valid_states:
            self._dependent_state = value.upper()
        else:
            self._dependent_state = 'UNKNOWN'
            self.LOG.warn('Impact Trigger dependent state should be one of {} (using {}).'.format(self.valid_states, self._state))

    @property
    def valid_states(self):
        """Return valid states depending on policy type"""
        return {'AVAILABILITY': self._avail_states,
                'PERFORMANCE': self._perf_states,
                'CAPACITY': self._cap_states,
                }.get(self.policy)

    def get_trigger(self):
        """Return arguments for Trigger object"""
        msg = '{state} when {threshold}% device {state}'.format(
                 state=self.state,
                 threshold=str(self.threshold))

        return (msg, self.trigger, self.policy, {'dependentState': self.dependent_state,
                                                 'threshold': str(self.threshold),
                                                 'state': self.state,
                                                 'metaTypes': [self.class_spec.meta_type],
                                                 }
                )

