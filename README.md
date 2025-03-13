# sponsors-bot

A Discord Bot that allows users to verify their GitHub Sponsors status and get access to sponsor-only roles/channels. It can also detect contributors to a GitHub repository and assign them a contributor role.

It works by prompting the user in a private thread to connect their GitHub account in Discord connection settings (even if it's not publicly visible on their Discord profile). The bot will then check if the user is a sponsor of the specified GitHub user and if so, assign the appropriate roles. It then stores this information in an PostgreSQL database.
