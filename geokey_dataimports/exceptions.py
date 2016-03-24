"""All exceptions for the extension."""

from django.utils.safestring import mark_safe


class FileParseError(Exception):
    """Throw file parsing error."""

    def __init__(self, message, errors):
        """Initialise error messages."""
        self.message = message
        self.errors = errors

    def to_html(self):
        """Convert error messages to HTML."""
        html = '<p>%s</p>' % self.message

        if self.errors:
            html += '<ul>'
            for error in self.errors:
                line = error.get('line')
                if line:
                    html += '<li>Line: %s</li>' % error.get('line')
                for message in error.get('messages'):
                    html += '<ul>'
                    html += '<li>%s</li>' % message
                    html += '</ul>'
            html += '</ul>'

        return mark_safe(html)
