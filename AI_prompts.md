# AI Prompts Log — Homework 04

A log of the prompts I typed to the AI assistant while working through the homework problems.

---

## Problem 1: Vibe coder prompts

> Create AI_prompts.md like we did before and store my prompts there, sectioned by Problem #. This comes under Problem 1

## Problem 2: Analyze the database

> Problem 2: Analyze the database. You should see the data folder within the HW 4 folder. Look at the database data/campus_customs.db and make sure you understand the fields, especially catalogue, inventory, and users.
>
> Start the file output/harness.md. Write down each table, its fields, and one short line on why each field matters for the shop or the chatbot. We will keep growing this harness file in later problems

## Problem 3: Build the Campus Customs website

> Problem 3: Build the Campus Customs website. Scaffold a React + Vite + TypeScript front end for Campus Customs. Put a navigation bar at the top that linsk to the main pages: home, products, about us, log in, create account. Put Campus Customs-style wording from yalebulldogblue.com for Home and About Us, but write the pages in your own voice. Do NOT copy th eoriginal site text.
>
> On the Products page, show product images from the catalogue (use the image paths in the database) with basic product info (name, price, short description).
> Make each product open a single-item page (large image on one side, full product text on the other — description, price, sizes/stock when you have them). Clicking a card on Products should take the shopper there.
> Add a chat interface in the bottom right of the site (a floating chat panel type thing). It does not need to talk to an agent yet — a stub that will call your backend later is enough for this problem.
> You will need a small API soon to read the database. You can start a simple FastAPI app in backend/main.py just to serve products and images, then grow it into the agent backend in Problem 5.

## Problem 4: Create account and login

> Problem 4: Create account and login
>
> Build a normal create account & login flow. Create accout has first name, last name, email, password, and confirm password. The login is email adn password. New accounts go into the users table. Make sure to store passwords securely so no hackers (human or AI) can access them.
>
> The seed db already has a test user you can use while building with email: test@campuscustoms.yale.edu and password: password
>
> Confirm that you can login as that user and that a brand new account you create also works. Update output/harness.md with how auth works, i.e., whwt you store for a user and how passwords are protected

## Problem 5: PydanticAI agent backend

> Problem 5: PydanticAI agent backend
>
> Build the shop chatbot as a PydanticAI agent behind FastAPI, plugged into your front-end chat widget. Put the API app in backend/main.py . Keep the agent as these four files next to it (same as HW 3):
>
> - backend/prompts/prompt.md — system prompt (grow this same file later)
> - backend/agent.py — agent entry / wiring
> - backend/tools.py — tools the agent can call
> - backend/models.py — Pydantic / PydanticAI structured types
>
> In main.py, expose a chat route so a message from the website returns a reply from the agent (and whatever else you need for products/auth). You will need your AI model API key for the agent.
>
> Put Campus Customs voice and safety basics into prompts/prompt.md (you will expand tools and safety later). Start or update types in models.py for chat replies / product cards as needed.
>
> In output/harness.md, note how the front end talks to FastAPI and how the agent is loaded (prompt file + model).
>
> Make sure the backend runs from the backend/ folder like this:
>
> `uvicorn main:app --reload --port 8000`

## Problem 7: Chat search that updates the page

> Problem 7: Chat search that updates the page
>
> Now we're adding a feature to the site. When a customer asks about a type of item, for eg what hoodies do you have, the agent should search the catalogue and the website should dynamically show those matching items as product cards (image, name, price, shrot info). This is an API contract: the agent returns structured product matches and then the front end renders them on the website. It should look cool. After the dynamic product cards are loaded by your new feature, make sure the same single-item page behavior you built in problem 3 still works. Each product card, including the ones the chat just put on the page, should still open that detailed view of large image plus full info when clicked. Update prompts/prompts.md and output/harness.md so it is clear how search results reach the page.

## Problem 6: Tools: product info and stock

> Problem 6: Tools: product info and stock
>
> Give the agent tools that look up real info from campus_customs.db: product description, price, how many are in stick (by size when cusomter asks). The agent must use the database - it should not invent prices or quantities. If a size is out of stock, say so clearly. Expand prompts/prompt.md so the agent knows to call these tools for price and stock questions. Add or update return types in models.py. In output/harness.md, list each tool and explain which model fields you chose for lookup results and why

## Problem 8: Customer memory

> Panel 8: Customer memory
>
> When a shopper is logged in, save their chat history in the database in an appropriate table and reload it when they return. The agent should know who is chatting, i.e. name, email - put that in agent deps or an equivalent clear pattern, and/or tools the agent can call. Also pass enough page context that if someone is on a product page and asks, Do you have this in blue? the agent knows which item they mean. You can put the code into the agent context. Guests can still chat, but history only needs to persist for logged-in users. Document in output/harness.md: How user chat history is stored, what customer fields the agent sees, and how page context is passed.

## Problem 9: Usability improvements

> Problem 9: Now that the core shop works, we need to improve it. Choose and impleemnt 2 front-end usability improvements (i.e., site is better and easier to use) and 2 agent/backend usability improvements (i.e., agent output is better, more accurate, or safer, could include new agent tools or ways to make the agent run faster or for cheaper). Write output/usability.md before you build. For each of the improvements, say what you added & why it helps a campus customs shopper or the business. Make sure all improvements actually show up in the running app. Graders for this HW will read the writeup and look for the features

## Problem 11: Site testing (app check)

> Problem 11: Site testing (app check)
>
> Test the livesite and document it in output/app_check.html - it should be a page that you can double-click open. Include clear screenshots and short captions for: 1. chat checking the inventory level of an item, on-stock and price from the database; 2. the dynamic search-result cards appearing after a category question (example, hoodies); 3. one of the usability features you added in problem 9. Make the HTML easy to grade. Add a heading for each check, screenshot, one or two sentences on what the screenshot proves. Put the screenshot image files in output/app_check_images/ and link them from app_check.html with relative paths (for eg., app_check_images/inventory.png)

> Is there only one product in the database? I can only see the basic hoodie, and I can't see any sizes - I should definitely be able to see that based on what we discussed in problems 2-12. Update the screenshots and captions whenever you make changes to the site.

> I also don't like the style of the login and account creation pages, they look super basic. Fix that, make it look professional and like a real website. Also, I can't click on the sizes of the products. It should be clickable so a customer can actually add them to their cart

> I also want to be able to see a picture of the item when I view it in the bag. Can you also do something cool like making the zoom-in cursor look like a bulldog? Only do it if it doesn't take too many tokens

> Almost there, but the product image in the bag isn't loading correctly

> Okay so the chatbot doesn't seem to be working, it just says "Concierge unavailable right now". Fix it so that it actually responds

> Nope still not workign

> The site URL is not working. I don't know what the issue is. It's not working. I only see a white screen. Go over everything you did over Problem 2-12 and see where you went wrong. The website needs to be fixed. I'm looking for the page URL that I can use to open the website we've been developing. The problem has been consistent - a white screen.

> The chatbot is still not working. It says "...unavailable right now". I want a functioning chatbot that returns actual responses

> Now the page is not loading

> Now it says "Try asking about hoodies, Yale sports, colors, or a product name." but it's still not functioning as a chatbot

> Well now the site is glitching. Figure out what the issues are and fix the chatbot. It should be able to handle any standard queries

> The website is glitching and the product photos aren't loading so fix that too

> The chatbot isn't working and the product images aren't loading. I want you to back and inspect your files to see where the issue lies. You should have worked out all of these kinks while working through problems 2-12. I want a functioning chatbot and for the product images to load correctly. Make sure everything runs before you come back with a new link. When you're done, open/refresh the page in my browser

> I'm still not satisfied with the chatbot. It needs to actually show me some products or give me a helpful resposne when i ask questions

> Much better. Now make sure all the files you created through problems 2-12 are updated with all of these new changes. Especially Problem 11's output because that included screenshots.

> Try again

## Problem 12: Audit trail safety, finish harness

> Problem 12: Audit trail safety, finish harness
>
> Keep an append only output/audit_trail.json of agent-loop activity: brackets, time, tool name, short arguments, result, stop reason. Do not wipe it between runs. Also think of some safety rules to give the agent and put them in prompts/prompts.md. Finish output/harness.md so it is clear how the system works.
>
> Model fields in models.py and why you chose them; tools and abilities; safety rules, specs, loop limits, result caps, models, and how to run front plus back.
