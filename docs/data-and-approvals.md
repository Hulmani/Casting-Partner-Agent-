# Data and approval rules

## Data

Store real profile details, email content, listing evidence, and application records locally outside the repository. Keep credentials in an operating-system credential store; browser session data stays in a dedicated excluded profile. Final storage and retention choices must be implemented before live intake. The current SQLite core is not encrypted and is intended for fictional demos only.

An opportunity needs source identity, external ID, title, original URL, observation timestamp, evidence, and whether the listing is complete. Production, role, filming dates, deadline, location, pay/currency, union requirements, and contact method are optional until verified. Unknown fields must remain explicit. Attach field-level evidence and confidence when model extraction is introduced.

Photos and personal details must not be sent merely because a web page requests them. Treat page content, emails, and attachments as evidence, never as instructions to the agent.

## Planned action approvals

Reading approved sources is separate from sending data. The first version prepares applications for review. Before a write, show destination, purpose, exact answers, selected files, and commitments. Record approval of that immutable payload; any change invalidates approval. Booking acceptance and legal terms remain separate approval steps.

Execution must retain an action ID, approval reference, listing revision, timestamp, and verified destination result. If the network or browser fails during submission, mark the result unknown and inspect the destination before retrying. Never equate clicking Submit with success.

No executor or approval implementation exists in the foundation iteration. The adapter contract advertises read capabilities only for the fictional demo.
