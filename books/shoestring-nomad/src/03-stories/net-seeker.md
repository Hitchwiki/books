# Net seeker

So, I've been thinking about this for a while now: Why isn't there a TRUE WiFi finder dongle thingy (is there? I've never heard of one...) What I'm thinking of us not simply something which senses the existence of a wifi signal, but finds and tests open, unlocked WiFi 'automatically.' Basically, I'm thinking of using a wifi module tied to an 8-bit micro with a push-button and a tri-color LED as a status indicator, running off of whatever necessary battery source (Recharable LiIon via USB?)
It would work something like this:
Push "Search"
LED=Red
uC gets a list from WiFi module of open (unsecure) access points
IF access points exist, LED=Orange
begin testing access points for connection
IF connection & IP address established, LED=Yellow
IF successful, attempt to ping a website (google? Casarobino? time.com?) LED=Yellow Blinking
IF successful (receives some correct response from website, indicating established connection to correct site), LED=Green
And bam, an indicator for available wifi. It would not be difficult ot add an LCD to indicate the SSID, but even that may be unnecessary. I'm just tired of wasting battery life turning on my N800 or pulling my laptop out of standby to find out the wifi is all encrypted/inaccessible.
Feedback? does something like this exist? Anyone interested in helping out (I should be able to do everything, but always love group projects/feedback)? I'll be putting together an electronics workbench when I get back to CT at my parents place.

---

Source: https://casarobino.org/2009/08/net-seeker
