EventFeedsProject is a fully automated calendar feed generator for live event venues, built for venue staff and managers to track local gig impacts.

It takes a single master_events.txt file with structured event data and auto-generates:

📁 .ics calendar feeds (1 per area)

📁 .txt reference files (for logs, auditing, or debugging)

📄 feeds_index.txt with links to each generated feed

Everything updates automatically using GitHub Actions, and is deployable to Netlify or GitHub Pages.

⚙️ How It Works
✅ 1. Add your events to data/master_events.txt
Each line in the file follows this format:

txt
Copy
Edit
Date | Artist | Ticket URL | Area | Venue | Capacity | Doors Open | Start | End | Description | Status | Notes | Busyness Start | Busyness End | Closest Tube
✅ 2. GitHub Actions runs on push
Every time you push a change to the data file, the system:

Splits events by area (e.g., Camden, Shepherd’s Bush)

Generates .ics files for each area

Writes .txt versions of each split

Outputs a feeds_index.txt with live feed URLs

📦 Output Structure
lua
Copy
Edit
output/
├── txt/
│   └── Shepherds_Bush_Events.txt
├── ics/
│   └── Shepherds_Bush_Events.ics
└── feeds_index.txt
🛠 Local Impact Format (in .ics files)
Each calendar event includes a custom "📊 Local Impact" block, with:

plaintext
Copy
Edit
📍 Venue: O2 Shepherd’s Bush Empire (Capacity: 2000)
🚉 Access: Shepherd’s Bush Market (Tube) / Shepherd’s Bush (Bus)
🚪 Doors: 19:00–19:45
🎟️ Tickets: https://ticketmaster.co.uk/...
🔥 Busyness: 18:30 – 21:00
🗒️ Notes:
• Sold out
• VIPs in attendance
This is optimized for:

FOH teams

Duty managers

Area leads

Event ops coordination

🚀 Getting Started
Fork or clone this repo

Add your events to data/master_events.txt

Push changes — GitHub Actions takes care of the rest

Deploy the output/ics/ folder to Netlify, Vercel, or GitHub Pages

📤 Deployment Tip
Want to subscribe to a feed in Apple/Google Calendar?

Deploy the repo to Netlify

Subscribe to .ics links from feeds_index.txt

Example:

ruby
Copy
Edit
https://your-netlify-site.netlify.app/output/ics/Shepherds_Bush_Events.ics
📚 Example Entry
txt
Copy
Edit
2025-11-01 | Peter Murphy | https://ticketmaster.co.uk/peter-murphy | Shepherd’s Bush | O2 Shepherd’s Bush Empire | 2000 | 19:00 | 19:30 | 23:00 | Celebrating David Bowie | Sold Out | VIPs attending; Late finish | 18:30 | 21:00 | Shepherd’s Bush Market
📂 Project Structure
txt
Copy
Edit
calendar_builder.py         # Main script
data/master_events.txt      # Input file (you edit this)
.github/workflows/build.yml # GitHub Actions runner
output/                     # Auto-generated feeds
🧠 To-Do / Ideas
 Add venue → Tube/Bus route mapping from venues.json

 Auto-highlight "Sold Out" with 🚨

 Add delivery timing + back-of-house flags

 iCal sync dashboard UI

👨‍💻 Built by Daniel Becker
Feedback, feature requests, or questions? Open an issue or DM me via GitHub.

