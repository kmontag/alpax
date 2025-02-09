# Manages configuration for this repository.
#
# Note that some apps should also be manually installed for the repository (it's currently not
# possible to manage these via terraform for non-organization owners):
#
# - https://github.com/apps/semantic-prs/
# - https://github.com/apps/codecov/

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

data "github_rest_api" "rulesets" {
  endpoint = "/repos/${var.github_owner}/${github_repository.default.name}/rulesets"

  lifecycle {
    postcondition {
      condition     = self.code == 200
      error_message = "Expected status code 200, but got ${self.code}"
    }
  }
}

locals {
  # Array containing entries like:
  #
  #  {"id": 12345, "name": "some name", ...}.
  #
  rulesets = jsondecode(data.github_rest_api.rulesets.body)

  # Get the existing main ruleset ID. This will be used to import the ruleset resource.
  #
  # If the ruleset ever gets deleted for some reason, this will be `null`, and the associated import
  # block can simply be commented out temporarily.
  main_ruleset_name = "main"
  main_ruleset_id   = one([for ruleset in local.rulesets : ruleset.id if ruleset.name == local.main_ruleset_name])
}

resource "github_repository_ruleset" "main" {
  name        = local.main_ruleset_name
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

# Import statements allowing the entire workspace to be imported from scratch. When creating new
# resources during development, some of these may need to be temporarily commented out.
import {
  to = github_repository.default
  id = var.github_repository_name
}

import {
  to = github_repository_ruleset.main
  id = "${github_repository.default.name}:${local.main_ruleset_id}"
}
