import hashlib

from rest_framework.throttling import SimpleRateThrottle


class MultiIdentityRateThrottle(SimpleRateThrottle):
    scope = None

    @staticmethod
    def parse_rate(rate):
        if rate is None:
            return None, None

        requests, period = rate.split("/")
        period = period.strip().lower()
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        if period[0].isdigit():
            multiplier = int(period[:-1])
            unit = period[-1]
        else:
            multiplier = 1
            unit = period[0]
        if unit not in units:
            raise ValueError(f"Unsupported throttle period: {period}")
        return int(requests), multiplier * units[unit]

    def get_cache_keys(self, request, view):
        raise NotImplementedError

    def allow_request(self, request, view):
        if self.rate is None:
            return True

        self.key = None
        self.history = None
        self.now = self.timer()
        cache_keys = self.get_cache_keys(request, view)
        if not cache_keys:
            return True

        histories = []
        for key in cache_keys:
            history = self.cache.get(key, [])
            while history and history[-1] <= self.now - self.duration:
                history.pop()
            if len(history) >= self.num_requests:
                self.key = key
                self.history = history
                return self.throttle_failure()
            histories.append((key, history))

        for key, history in histories:
            history.insert(0, self.now)
            self.cache.set(key, history, self.duration)
        return True

    @staticmethod
    def _identity_key(scope, identity):
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        return f"throttle_{scope}_{digest}"


class SignupEmailThrottle(MultiIdentityRateThrottle):
    scope = "signup_email"

    def get_cache_keys(self, request, view):
        email = request.data.get("email", "")
        ident = self.get_ident(request)
        if not isinstance(email, str):
            email = ""
        return [
            self._identity_key(self.scope, f"ip:{ident}"),
            self._identity_key(self.scope, f"email:{email.strip().casefold()}"),
        ]


class PasswordForgotThrottle(MultiIdentityRateThrottle):
    scope = "password_forgot"

    def get_cache_keys(self, request, view):
        school_id = request.data.get("school_id", "")
        ident = self.get_ident(request)
        if not isinstance(school_id, str):
            school_id = ""
        return [
            self._identity_key(self.scope, f"ip:{ident}"),
            self._identity_key(
                self.scope,
                f"school_id:{school_id.strip().casefold()}",
            ),
        ]


class PasswordVerifyThrottle(MultiIdentityRateThrottle):
    scope = "password_verify"

    def get_cache_keys(self, request, view):
        school_id = request.data.get("school_id", "")
        ident = self.get_ident(request)
        if not isinstance(school_id, str):
            school_id = ""
        return [
            self._identity_key(self.scope, f"ip:{ident}"),
            self._identity_key(
                self.scope,
                f"school_id:{school_id.strip().casefold()}",
            ),
        ]
