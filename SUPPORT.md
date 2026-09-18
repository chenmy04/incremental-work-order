# Support

## Where to go

| You want to… | Go to |
| --- | --- |
| Ask how to apply the workflow to your project, or show what you built with it | **GitHub Discussions** (`Q&A` / `Show and tell`) |
| Report that a rule, template or the validator misbehaves | [Issues → Bug report](https://github.com/mmm-05610/incremental-work-order/issues/new?template=bug_report.yml) |
| Propose a change to the model | [Issues → Feature request](https://github.com/mmm-05610/incremental-work-order/issues/new?template=feature_request.yml) |
| Report that the workflow behaves differently on a specific agent/tool | [Issues → Platform support](https://github.com/mmm-05610/incremental-work-order/issues/new?template=platform_support.yml) |
| Report an unsafe rule or a gate that cannot fail | **Security → Report a vulnerability** (private), see [SECURITY.md](SECURITY.md) |

Before filing, a quick look at [SKILL.md](SKILL.md) answers most "how should I…" questions; the
[examples/](examples/) directory shows a filled-in order.

## What is not supported here

- **Your project's environment**: credentials, infrastructure, CI, or the code the orders change. This repo is a
  workflow; it cannot debug an adopter's tree.
- **Custom forks of the rules**: if you changed `SKILL.md` locally, say so in the report, otherwise answers will
  assume upstream behaviour.
- **Guarantees about model compliance**: the workflow exists because instruction-following is not a guarantee.
  If a check is missing or bypassable, that is a bug (report it); if a model ignored a rule, that is expected
  behaviour the design already accounts for.

## Response expectations

Maintained by one person on a best-effort basis. Issues are triaged when seen; security reports take priority.
No SLA, no guaranteed fix window, no bounty programme.
