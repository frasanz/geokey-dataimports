"""All helpers for the context."""


def does_not_exist_msg(title):
    """
    Make the message when something does not exist.

    Parameters
    ----------
    title : str
        Title to set to the message.

    Returns
    -------
    str
        Message with a title.
    """
    return '%s matching query does not exist.' % title
