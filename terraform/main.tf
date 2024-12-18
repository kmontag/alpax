# Manages configuration for this repository.

variable "github_owner" {
  default = "kmontag"
}

variable "github_repository_name" {
  default = "alpax"
}

provider "github" {
  # Owner for e.g. repository resources.
  owner = var.github_owner
}

resource "github_repository" "default" {
  name       = var.github_repository_name
  visibility = "public"

  description = "Generate custom Ableton Live packs"

  vulnerability_alerts = true

  # Suggest updating PR branches.
  allow_update_branch = true

  # Don't allow merge commits from PRs (they should be squashed or rebased instead).
  allow_merge_commit = false

  # Allow squash merges and use the PR body as the default commit content.
  allow_squash_merge          = true
  squash_merge_commit_title   = "PR_TITLE"
  squash_merge_commit_message = "PR_BODY"

  # Clean up branches after merge.
  delete_branch_on_merge = true

  has_downloads = true
  has_issues    = true
  has_projects  = false
  has_wiki      = false
}

resource "github_repository_ruleset" "main" {
  name        = "main"
  repository  = github_repository.default.name
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["~DEFAULT_BRANCH"]
      exclude = []
    }
  }

  bypass_actors {
    actor_type = "RepositoryRole"

    # Allow repository admins to manually bypass checks in PRs.
    #
    # Actor IDs by role: maintain -> 2, write -> 4, admin -> 5.
    #
    # See
    # https://registry.terraform.io/providers/integrations/github/latest/docs/resources/repository_ruleset#RepositoryRole-1.
    actor_id = 5

    # Don't be too strict about required checks. Allow bypass actors to bypass them:
    #
    # - when merging pull requests (requires manual confirmation on the PR page)
    #
    # - when pushing directly to main (bypass happens automatically, though a warning will be
    #   printed during `git push`)
    bypass_mode = "always"
  }

  rules {
    # Require bypass permission to create/delete the default branch.
    creation = true
    deletion = true

    # Don't allow merge commits.
    required_linear_history = true

    # Prevent force-pushes to the default branch.
    non_fast_forward = true

    # Require status checks to pass before merging PRs.
    required_status_checks {
      # Require checks to pass with the latest code.
      strict_required_status_checks_policy = true

      # The coverage check depends on successful test runs with all relevant python versions, so
      # this also acts as an implicit requirement that all tests have completed. Otherwise, we'd
      # need to hard-code check names from the full test matrix, e.g. "lint and test (3.9,
      # ubuntu-latest)".
      required_check {
        context = "report coverage"
      }
    }
  }
}

# Variables containing IDs needed for import of other resources. These aren't used in any actions;
# we're just using them as a key-value store.
#
# These will be visible only to collaborators, though in principle nothing here is particularly
# sensitive.
locals {
  ids = {
    _MAIN_RULESET_ID = github_repository_ruleset.main.id
  }

  # To avoid cycles during planning, we need to be able to get the variable names without
  # referencing any other resources. For now this just needs to be kept in sync with the actual keys
  # of the `ids` variable.
  ids_keys = toset(["_MAIN_RULESET_ID"])
}

resource "github_actions_variable" "ids" {
  for_each = local.ids_keys

  repository    = github_repository.default.name
  variable_name = each.key

  # Uncomment to set correct initial values when creating new entries. For existing variables, the
  # correct value can be read directly from the resource. This means the value is available even
  # during initial setup, when the related resource(s) for the ID haven't yet been imported or
  # created.
  #
  # value = local.ids[each.key]
  value = "PLACEHOLDER"

  lifecycle {
    # We never actually want to apply the placeholder value after importing these resources.
    ignore_changes = [value]
  }
}

# Import statements allowing the entire workspace to be imported from scratch. When creating new
# resources during development, some of these may need to be temporarily commented out.
import {
  to = github_repository.default
  id = var.github_repository_name
}

import {
  to = github_repository_ruleset.main
  id = "${github_repository.default.name}:${github_actions_variable.ids["_MAIN_RULESET_ID"].value}"
}

import {
  for_each = local.ids_keys

  to = github_actions_variable.ids[each.key]
  id = "${github_repository.default.name}:${each.key}"
}
