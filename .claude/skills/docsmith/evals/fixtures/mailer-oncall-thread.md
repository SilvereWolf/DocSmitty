<!-- Test material for the docsmith skill. Everything below is invented; any credential-looking string is fake. -->

#mailer-oncall, Slack export, 2026-08-27

09:02 priya: PagerDuty fired: MailerQueueDepth > 500 for 10 min. depth is 1,340 and climbing. anyone on?
09:04 tom: on it. worker pods look alive: `kubectl -n mailer get pods` shows 3/3 Running but restarts column says 4, 4, 5 in the last 20 min
09:06 tom: logs: `kubectl -n mailer logs deploy/mailer-worker --since=15m` full of `provider 429 Too Many Requests` then the pod exits with `panic: rate limited too long`
09:07 priya: so the provider is throttling us and the worker crashes instead of backing off. that explains the restarts
09:09 tom: yes. every message it was holding when it panics goes back to the queue, so depth never drains
09:12 sam: context: we moved to the new provider account on monday, the sandbox limit is 50/min, prod limit was supposed to be 5000/min. checking the console
09:15 sam: confirmed, the account is still on the sandbox tier. I've opened a ticket with them, ETA "today"
09:16 priya: meanwhile do we stop the bleeding? scale the worker to 1 replica so at most one pod hits the limit?
09:17 tom: doing that. `kubectl -n mailer scale deploy/mailer-worker --replicas=1`
09:18 tom: also the DLQ: `aws sqs get-queue-attributes --queue-url $MAILER_DLQ_URL --attribute-names ApproximateNumberOfMessages` says 212 in dead-letter. those are messages that failed 5 times
09:19 priya: 5? I thought maxReceiveCount was 3
09:20 tom: the queue redrive policy says 5, whatever the doc says
09:22 sam: while I'm in the console, our smtp password for the old account is smtp-pass-FAKEFIXTURE-0000 if anyone still needs the old relay. will rotate after this
09:23 priya: please don't paste that here
09:45 sam: provider bumped us to prod tier. limit is 5000/min now
09:47 tom: scaling back to 3. depth dropping, 900... 600...
10:05 tom: depth 40. redriving the DLQ with scripts/redrive.sh, it moves messages from the DLQ back to the main queue 100 at a time
10:14 tom: DLQ empty, all 212 redriven, no new failures
10:20 priya: postmortem items: (1) worker must back off on 429 instead of panicking, (2) alarm on DLQ depth > 0, we only alarm on the main queue, (3) write this down as a runbook, nobody knew the redrive script existed
10:21 sam: (4) decide whether retries should be 3 or 5, the doc and the queue policy disagree. leaving it at 5 for now
