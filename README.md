# Agent Skills

A collection of reusable agent skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and other AI coding assistants. Each skill is a self-contained module with scripts, references, and configuration that extend an AI agent's capabilities.

## Quick Start

### Option 1: Copy individual skill

```bash
# Copy a skill into your project
cp -r skills/<skill-name> /path/to/your/project/.claude/skills/

# Configure environment
cd /path/to/your/project/.claude/skills/<skill-name>
cp .env.example .env
# Edit .env with your credentials
```

### Option 2: Git submodule (all skills)

```bash
git submodule add https://github.com/user/agent-skills.git .claude/agent-skills
```

Then symlink or copy the skills you need into `.claude/skills/`.

## Available Skills

| Skill | Description | Tools |
|-------|-------------|-------|
| [gitlab-self-hosted](skills/gitlab-self-hosted/) | GitLab Server MR workflow via REST API v4 - get/create MRs, assign reviewers, post reviews, analyze changes, staging merge, test case generation | `curl`, `jq` |

## Skill Structure

Each skill follows a consistent structure:

```
skills/<skill-name>/
├── SKILL.md          # Metadata (YAML frontmatter) + argument handling instructions
├── README.md         # Human-readable setup guide and usage docs
├── .env.example      # Environment variables template (copy to .env)
├── scripts/          # Executable bash/python scripts
└── references/       # Reference docs consumed by the AI agent at runtime
```

### Key Files

- **SKILL.md** - The entry point for AI agents. Contains YAML frontmatter (`name`, `description`, `version`, `license`, `allowed-tools`) and argument routing table.
- **README.md** - Setup instructions, usage examples, and workflow documentation for humans.
- **.env.example** - Template for required environment variables. Never commit `.env` files.
- **scripts/** - Self-contained scripts that handle API calls, data processing, etc.
- **references/** - Markdown docs that the AI agent reads for context (API specs, workflows, best practices).

## Contributing

1. Create a new directory under `skills/` with a descriptive kebab-case name
2. Add `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: my-skill
   description: What this skill does
   version: 1.0.0
   license: MIT
   allowed-tools:
     - Bash
   ---
   ```
3. Add `README.md` with setup and usage instructions
4. Add `.env.example` if the skill requires credentials or configuration
5. Add executable scripts in `scripts/` and reference docs in `references/`
6. Ensure `.env` is in `.gitignore` (already configured at repo root)

## Security

- **Never commit `.env` files** - they contain credentials and tokens
- The root `.gitignore` blocks all `.env` files by default
- Each skill provides `.env.example` as a safe template
- Use scoped tokens with minimal required permissions

## License

MIT
