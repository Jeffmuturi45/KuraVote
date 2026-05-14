# KuraVote System Improvement Review

This review highlights practical enhancements for reliability, security, and performance.
The highest-impact items from this review have been implemented in this branch.

## Implemented in this branch

1. **Environment-safe configuration**
   - `SECRET_KEY` is now required in non-debug, non-test environments.
   - `ALLOWED_HOSTS` can now be configured through a comma-separated `ALLOWED_HOSTS` environment variable.
   - Tests and local development can run without a configured MySQL database by falling back to SQLite.
   - HTTPS-only cookie and redirect settings remain enabled for production but are disabled during tests.

2. **Faster live results API**
   - Candidate vote counts are now calculated with a queryset annotation instead of calling `vote_count` and `vote_percentage` properties per candidate.
   - This reduces repeated database queries as candidate lists grow.

3. **Fresh results after voting**
   - Casting a vote now invalidates the cached results response for that election immediately.
   - Admin live results no longer have to wait for the cache timeout before reflecting a newly cast vote.

4. **Regression coverage**
   - Tests now verify that a successful vote clears the cached results payload.
   - Tests now verify that the results API returns annotated vote totals and percentages correctly.

## Recommended next enhancements

1. **Election lifecycle enforcement**
   - Centralize active-election lookup so all views consistently enforce `status`, `start_date`, and `end_date`.
   - Prevent activation of elections whose voting window is not currently open unless an admin explicitly overrides it.

2. **Admin audit trail expansion**
   - Record important actions such as election activation/closure, candidate edits, student deactivation, password resets, and CSV imports in a first-class audit model.
   - Include actor, timestamp, target object, IP address, and a concise action summary.

3. **CSV import hardening**
   - Validate email format during row parsing, not only at the model/form level.
   - Produce a downloadable error report for skipped rows so admins can correct CSV files faster.
   - Consider moving large imports to a background job if deployment later supports a queue.

4. **Results-query reuse**
   - Extract the annotated results aggregation used by API, reports, PDF export, and Excel export into a shared service.
   - This would reduce duplicated counting logic and keep all result surfaces consistent.

5. **Operational readiness**
   - Add a production deployment checklist covering required environment variables, `collectstatic`, HTTPS, database backups, and scheduled database maintenance.
   - Add health-check endpoints for uptime monitoring.

6. **Security monitoring**
   - Store login attempt metadata for admins to review repeated failed logins by admission number and IP.
   - Consider more generic login failure messages to reduce account enumeration risk.
