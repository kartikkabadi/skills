# Agent Skills

A curated collection of 57 reusable skill definitions for AI coding agents. Each skill is a `SKILL.md` file that teaches an agent a specific capability — from design taste to cloud infrastructure to secure coding practices.

This is a **mixed-provenance collection**: some skills are Kartik's original work, while others are exact or adapted imports preserved under their upstream licenses. The repository is not licensed as one blanket MIT work. See [`skills.provenance.json`](skills.provenance.json), [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md), and [`DISTRIBUTION.md`](DISTRIBUTION.md).

## What are skills?

Skills are structured prompts that load domain-specific expertise into an AI agent's context. When a task matches a skill's trigger, the agent reads the `SKILL.md` file and gains focused knowledge, conventions, and procedures for that domain. They work across any agent harness that supports skill loading (Claude Code, Codex, Cursor, OpenClaw, etc.).

## Skills included

### Development Practices
| Skill | Description |
|-------|-------------|
| `clean-code` | Original practical clean-code rules for maintainable software |
| `diagnose` | Disciplined diagnosis loop for hard bugs and regressions |
| `tdd` | Test-driven development with red-green-refactor |
| `how-to-code` | Prerequisite thinking discipline before coding |
| `review` | Two-axis code review (standards + spec) |
| `improve` | Codebase improvement planning |
| `improve-codebase-architecture` | Architecture-focused improvement |
| `repo-inspection` | Deep codebase understanding |
| `full-output-enforcement` | Complete code generation without stubs |

### Design & UI
| Skill | Description |
|-------|-------------|
| `high-end-visual-design` | Premium agency-quality web design |
| `design-taste-frontend` | Senior UI/UX engineering metrics |
| `gpt-taste` | Elite GSAP motion and UX |
| `image-to-code` | Website image-to-code implementation |
| `industrial-brutalist-ui` | Raw mechanical Swiss typographic interfaces |
| `minimalist-ui` | Clean editorial-style interfaces |
| `redesign-existing-projects` | Upgrade existing sites to premium quality |
| `stitch-design-taste` | Google Stitch design system |
| `brandkit` | Premium brand identity generation |
| `imagegen-frontend-web` | Premium web design direction images |
| `imagegen-frontend-mobile` | Premium mobile app screen concepts |

### Agent Workflows
| Skill | Description |
|-------|-------------|
| `handoff` | Agent-to-agent handoff documentation |
| `agent-input-trust` | Treat external content as evidence |
| `agent-verification-discipline` | Verify claims before asserting |
| `caveman` | Ultra-compressed communication |
| `prototype` | Throwaway prototyping for design exploration |
| `qa` | Interactive QA session workflow |
| `triage` | Issue triage through state machines |

### Writing
| Skill | Description |
|-------|-------------|
| `writing-shape` | Shape raw material into an article |
| `writing-beats` | Beat-by-beat narrative construction |
| `writing-fragments` | Mine raw material for article fragments |
| `edit-article` | Edit and improve articles |

### Planning
| Skill | Description |
|-------|-------------|
| `to-prd` | Convert conversation into a PRD |
| `to-issues` | Break plans into actionable issues |
| `grill-me` | Stress-test plans through interrogation |
| `grill-with-docs` | Challenge plans against existing domain model |

### Cloudflare
| Skill | Description |
|-------|-------------|
| `cloudflare` | Comprehensive Cloudflare platform |
| `cloudflare-email-service` | Transactional email with Cloudflare |
| `cloudflare-one` | Zero Trust and SASE |
| `durable-objects` | Stateful Durable Objects |
| `workers-best-practices` | Production Workers best practices |
| `wrangler` | Workers CLI deployment |
| `turnstile-spin` | Turnstile CAPTCHA setup |
| `web-perf` | Web performance analysis |
| `sandbox-sdk` | Sandboxed code execution |
| `agents-sdk` | Build AI agents on Cloudflare Workers |

### Security
| Skill | Description |
|-------|-------------|
| `supply-chain-install-protection` | Package manager supply chain security |
| `vibe-security` | Audit vibe-coded applications |
| `git-branch-worktree-discipline` | Safe git branch/worktree workflows |

### DevOps & Workflow
| Skill | Description |
|-------|-------------|
| `setup-pre-commit` | Husky pre-commit hooks |
| `opensrc` | Fetch dependency source code |
| `migrate-to-shoehorn` | TypeScript assertion migration |
| `scaffold-exercises` | Exercise directory scaffolding |

### Business & Product
| Skill | Description |
|-------|-------------|
| `telephony-product-architecture` | Phone call product design |
| `unit-economics-analysis` | SaaS unit economics analysis |

### Meta
| Skill | Description |
|-------|-------------|
| `find-skills` | Discover available agent skills (restricted internal-only) |
| `write-a-skill` | Create new skill definitions |
| `private-intelligence-reader` | Build personal intelligence readers |

## Usage

Each skill directory contains a `SKILL.md` file. Load them into your agent harness:

### Claude Code / Codex / Cursor

For private internal use from the repository root:

```bash
mkdir -p ~/.agents/skills
for skill_file in */SKILL.md; do
  cp -R "$(dirname "$skill_file")" ~/.agents/skills/
done
```

This includes the restricted internal-only skill. Do not publish or mirror the resulting directory wholesale. Public exports must follow [`DISTRIBUTION.md`](DISTRIBUTION.md) and exclude every manifest entry marked `restricted`.

### Safe public export

```bash
python3 scripts/verify_provenance.py
python3 scripts/export_public.py ./dist/public-skills
```

The exporter creates a self-contained 56-skill collection with the filtered provenance manifest, required upstream license texts, and generated notices. It refuses to include restricted entries.

### Direct loading
Skills are designed to be referenced by name. When you ask an agent to do something matching a skill's domain, reference the skill:

```
Load clean-code skill and review this code.
Use high-end-visual-design for this landing page.
Load cloudflare and deploy this Worker.
```

## Creating your own skills

See the `write-a-skill` skill in this repo, or copy one of the existing skills as a template. Each skill should focus on a specific domain and include:
- When to use this skill (trigger conditions)
- Core knowledge and conventions
- Procedures and workflows
- Examples where helpful

## License and provenance

The root [`LICENSE`](LICENSE) is MIT and applies only to original material identified with `"license_file": "LICENSE"` in [`skills.provenance.json`](skills.provenance.json).

Imported and adapted skills retain their pinned upstream licenses and attribution. Exact upstream license texts are preserved in [`LICENSES/`](LICENSES/), with a readable summary in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

`find-skills` is retained for private internal use but is **not redistributable from this repository** because its upstream source declares no license.
