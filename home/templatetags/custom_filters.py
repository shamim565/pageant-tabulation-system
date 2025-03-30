from django import template

register = template.Library()


@register.filter
def get_score(scores, candidate, criteria):
    """Returns the score for a given candidate and criteria."""
    return scores.filter(candidate=candidate, criteria=criteria).first()

@register.simple_tag
def filter_scores(scores, judge, round):
    """Returns filtered scores based on judge and round"""
    return scores.filter(judge=judge, criteria__round=round)

@register.filter
def score_for_criteria(scores, criteria_id, judge):
    return scores.filter(criteria_id=criteria_id, judge=judge).first()

@register.filter
def get_item(dictionary, key):
    if dictionary and key is not None:
        return dictionary.get(key, None)
    return None

@register.filter
def all_values_not_none(dictionary):
    """Returns True if all values in the dictionary are not None."""
    return all(value is not None for value in dictionary.values()) if dictionary else False

@register.filter
def get_attribute(value, arg):
    """Returns the attribute of an object (if dictionary, fetches the key)."""
    if isinstance(value, dict):
        return value.get(arg, None)
    return getattr(value, arg, None)