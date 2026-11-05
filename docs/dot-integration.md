# Optional dot integration (design only)

The standalone app must work without a ChatGPT dot. No dot connection, plugin, MCP server, or recurring task is implemented by this package.

A user with an eligible dot can assign it ongoing casting work using their authorized connected apps and browser. A dot's cloud browser has its own sessions; it does not inherit the user's local Chrome login. Some sites may require a connected computer or verification, so Facebook support must be tested rather than assumed.

If we later expose this app to a dot, use a narrow authenticated local plugin/tool interface for listing opportunities, reading source status, and preparing applications. Keep action execution behind the same immutable-payload approval checks as the standalone interface. Reading an instruction in a casting post must not grant authority to send data.

Do not expose an unrestricted shell, general desktop-control endpoint, personal data folder, or browser debugging port to the network. Connection, supported tools, user identity, local-computer availability, and revocation must be verified before enabling integration. A proposed interface is not an active connection.

Official references checked November 4, 2026:

- https://learn.chatgpt.com/docs/dots
- https://learn.chatgpt.com/docs/dots/computers-and-apps
