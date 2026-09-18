# Security Policy

## What this repository is

This repo is **documentation plus one dependency-free Python script**. It has no runtime, no network access, no
credential handling, no package dependencies, and it is never executed as a service. That makes the usual
supply-chain surface very small — which is exactly why the interesting reports here are of two kinds.

## In scope

1. **A documented rule that is unsafe to follow.** If the workflow, read literally by an agent, would let it:
   write outside its declared `write_paths`; merge into a mainline, push, or widen its own scope without the
   user's approval; treat credentials or protected paths as negotiable; or continue past a gate that cannot
   pass. Those are security bugs in the workflow, not style issues — please report them.
2. **A gate that cannot fail.** Any rule that claims to protect something but has no counter-example proving it
   rejects anything. `scripts/validate_order.py` is the executable part of this repo; a validator bypass (a
   conforming-looking order that should have failed, or a broken order that passes) is a real finding.
3. **Validator input handling.** `scripts/validate_order.py` reads files you point it at. Reports about crashes,
   hangs, or reads outside the given path in any realistic usage are welcome (it is not sandboxed, so it will
   obviously read any file you hand it).

## Out of scope

- Anything requiring the *consuming project's* code, credentials, or infrastructure — that is the adopter's
  environment, not this repo.
- Prompt-injection payloads aimed at a hosted service: there is no service here.
- Reports that a model "could" ignore the rules: the workflow's whole design assumes rules must be checkable
  precisely because instruction-following is not a guarantee. Bring a concrete case where a check is missing
  or bypassable, and it is in scope (see 1 and 2).

## How to report

Use GitHub's **private vulnerability reporting**: open the repository's *Security* tab → *Report a
vulnerability*. Please do not open a public issue for anything you believe is exploitable.

Include: what you expected, what happened, the smallest reproduction (a file, an order, a command), and the
version or commit you tested. If the issue is "the docs tell an agent to do X", quote the exact sentence.

## What to expect

Maintained by one person on a best-effort basis: acknowledgement when seen, an assessment with a fix or a
reason it is out of scope, and a note in `CHANGELOG.md` when a report changes the workflow. No bounty
programme, no SLA.
