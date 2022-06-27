""" Generic fields """
import datetime
import time

from xblock.fields import JSONField


class RelativeTime(JSONField):
    """
    Relative time serialized as "HH:MM:SS".

    JSON representation: "HH:MM:SS"
    Python representation: datetime.timedelta
    """

    MUTABLE = False

    @classmethod
    def isotime_to_timedelta(cls, value):
        """
        Convert integers and strings to the "HH:MM:SS" format.
        """
        try:
            # Convert integers into a formatted time string.
            value = int(value)
            value = time.strftime('%H:%M:%S', time.gmtime(int(value)))
        except ValueError as e:
            # Skip these -- we'll catch them below
            pass

        try:
            obj_time = time.strptime(value, "%H:%M:%S")
        except ValueError as e:
            raise ValueError(
                f"Incorrect RelativeTime value {value!r} was set in XML or serialized. "
                f"Original parse message is {e}"
            ) from e
        return datetime.timedelta(
            hours=obj_time.tm_hour, minutes=obj_time.tm_min, seconds=obj_time.tm_sec
        )

    def from_json(self, value):
        """
        Convert JSON value into Python representation.
        If not value, returns 0.
        If value is float (backward compatibility issue), convert to timedelta.
        """
        if not value:
            return datetime.timedelta(seconds=0)

        if isinstance(value, datetime.timedelta):
            return value

        return self.isotime_to_timedelta(value)

    def to_json(self, value):
        """
        Convert Python representation to JSON.
        If empty, returns "00:00:00".
        If float (backward compatibility), convert it.

        If value go over 23:59:59, raise an exception.
        """
        if not value:
            return "00:00:00"

        if isinstance(value, float):
            return self.timedelta_to_string(
                datetime.timedelta(seconds=min(value, 86400))
            )

        if isinstance(value, datetime.timedelta):
            if value.total_seconds() > 86400:
                raise ValueError(
                    "RelativeTime max value is 23:59:59=86400.0 seconds, "
                    f"but {value.total_seconds()} seconds is passed"
                )
            return self.timedelta_to_string(value)

        raise TypeError(f"RelativeTime: cannot convert {value!r} to json")

    def timedelta_to_string(self, value):
        """
        String representation of datetime.timedelta has [H]H:MM:SS format,
        which is not suitable for front-end (and ISO time standard),
        so we force HH:MM:SS format.
        """
        as_string = str(value)
        if len(as_string) == 7:
            as_string = "0" + as_string
        return as_string

    def enforce_type(self, value):
        """
        Ensure that when set explicitly the Field is set to a timedelta
        """
        if isinstance(value, datetime.timedelta) or value is None:
            return value

        return self.from_json(value)
