# Agent Skills

A collection of agent skills for Claude Code and other AI coding assistants.

## Installation

### Claude Code

Add a skill to your project:

```bash
# Copy skill folder to your project's .claude/skills/ directory
cp -r skills/<skill-name> /path/to/your/project/.claude/skills/
```

Or add as a git submodule:

```bash
git submodule add https://github.com/user/agent-skills.git .claude/agent-skills
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [gitlab-self-hosted](skills/gitlab-self-hosted/) | GitLab Server MR workflow via REST API v4 - get MR details, create MRs, assign reviewers, post code review comments, analyze changes |

## Skill Structure

Each skill follows this structure:

```
skills/<skill-name>/
├── SKILL.md          # Metadata + argument handling (YAML frontmatter)
├── README.md         # Setup guide and usage documentation
├── .env.example      # Environment variables template
├── scripts/          # Executable bash scripts
└── references/       # Reference documentation for the AI agent
```

## Contributing

1. Create a new directory under `skills/`
2. Add `SKILL.md` with YAML frontmatter (name, description, version, license, allowed-tools)
3. Add `README.md` with setup and usage instructions
4. Add `.env.example` if the skill requires configuration
5. Add scripts and references as needed

## License

MIT
