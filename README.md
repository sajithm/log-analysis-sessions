# log-analysis-sessions
Analyze web server log files to determine user sessions

Allows an approximation of the user sessions from the server logs. 
The visits from the same IP address and same user agent are considered to be part of the same session if the visit happens within a defined time period (30 minutes). 
If not, a new session is assumed.

If the session information can be obtained from other sources, use that instead (Duh!). If not, this might be helpful even though it might not be not totally accurate.
