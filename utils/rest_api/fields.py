from rest_framework import serializers
from rest_framework.fields import flatten_choices_dict, to_choices_dict


class LazyChoiceFieldMixin(object):
    """ """

    def __init__(self, *args, **kwargs):
        super(LazyChoiceFieldMixin, self).__init__(*args, **kwargs)
        self.channel = kwargs.get('channel', None)

    @property
    def context(self):
        context = super(LazyChoiceFieldMixin, self).context
        context['channel'] = self.channel
        return context

    @property
    def choice_strings_to_values(self):
        """
        Map the string representation of choices to the underlying value.
        Allows us to deal with eg. integer choices while supporting either
        integer or string input, but still get the correct datatype out.
        """
        return {key: key for key in self.choices}

    @property
    def grouped_choices(self):
        choices = self._choices
        if callable(choices):
            choices = choices(self.context)

        return to_choices_dict(choices)

    def _return_choices(self):
        return flatten_choices_dict(self.grouped_choices)

    def _get_choices(self):
        return self._return_choices()

    def _set_choices(self, choices):
        self._choices = choices

    choices = property(_get_choices, _set_choices)


class LazyChoiceField(LazyChoiceFieldMixin, serializers.ChoiceField):
    """"""


class ListLazyChoiceField(LazyChoiceField):
    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return ''

        if not isinstance(data, list):
            self.fail('invalid_choice', input=data)

        result = []
        choices = self.choice_strings_to_values.keys()
        for item in data:
            try:
                if isinstance(item, dict) and str(item.get('value')) in choices:
                    result.append(item)
                elif str(item) in choices:
                    result.append(item)
                else:
                    self.fail('invalid_choice', input=item)
            except (KeyError, TypeError):
                self.fail('invalid_choice', input=item)

        return result
