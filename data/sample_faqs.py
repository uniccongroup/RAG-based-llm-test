"""Sample FAQ data for Academy X."""

# Sample FAQs for testing and initial indexing
SAMPLE_FAQS = """
# Academy X FAQ - Enrollment & Admission

## Q: What are the requirements to enroll at Academy X?
A: Academy X is a tech training hub — there are no academic entry requirements like GPA or standardised test scores. All you need is:
- A passion for technology and willingness to learn
- Basic computer literacy (able to use a browser, keyboard, and file system)
- A stable internet connection for online/hybrid tracks
- Minimum age of 18 (or 16 with parental consent)
We welcome beginners, career-changers, and professionals looking to upskill.

## Q: How do I apply to Academy X?
A: Applying is straightforward:
1. Visit our website and select your desired track
2. Fill out the online application form (takes about 10 minutes)
3. Complete a short aptitude quiz (no coding knowledge required)
4. Attend a free 30-minute orientation session with an advisor
5. Confirm your spot by paying the enrolment deposit or arranging a payment plan
You will receive a decision within 48 hours of your orientation.

## Q: When do new cohorts start?
A: New cohorts kick off every month. Upcoming start dates are listed on our website. We recommend applying at least two weeks before your preferred start date to secure your place.

---

# Academy X FAQ - Programs & Tracks

## Q: What training tracks does Academy X offer?
A: We currently offer the following tech tracks:
- **Software Development** — Full-stack web development using Python, JavaScript, React, and Node.js
- **Data Science & AI** — Data analysis, machine learning, and AI model deployment
- **Cybersecurity** — Ethical hacking, network defence, and security operations
- **Cloud & DevOps** — AWS/Azure infrastructure, CI/CD pipelines, and containerisation
- **UI/UX Design** — User research, Figma prototyping, and product design
- **Product Management** — Agile methodology, roadmapping, and stakeholder management
All tracks include hands-on projects and real-world case studies.

## Q: How long are the programs?
A: Program duration depends on the track and learning mode:
- Bootcamp (intensive, full-time): 12 weeks
- Part-time (evenings and weekends): 6 months
- Self-paced (online): 3–12 months depending on your pace
All modes cover the same curriculum and lead to the same certificate.

## Q: Do I need prior coding experience to join?
A: Most tracks have a beginner-friendly entry path — no prior coding experience is needed. However, some advanced modules (e.g., Data Science or Cloud) move faster if you already have basic programming knowledge. Our advisors will help you choose the right entry point.

## Q: Are courses available online?
A: Yes. All tracks are available in three delivery modes:
- **In-person** at our training centres
- **Online (live)** — real-time classes via video conference
- **Hybrid** — mix of in-person workshops and online sessions
Recorded sessions are provided for all live classes so you can revise at your own pace.

---

# Academy X FAQ - Fees & Payment

## Q: How much do the programs cost?
A: Tuition varies by track and mode:
- Bootcamp (12 weeks, full-time): ₦450,000 / $300
- Part-time (6 months): ₦320,000 / $215
- Self-paced (online): ₦180,000 / $120
All fees include course materials, project tools, and career support. There are no hidden charges.

## Q: Do you offer payment plans or scholarships?
A: Yes. We offer:
- **Instalment plans** — split your tuition into 2 or 3 monthly payments at no extra cost
- **Income Share Agreement (ISA)** — pay nothing upfront; pay 10% of your salary for 12 months once you land a job earning above the threshold
- **Merit scholarships** — up to 40% discount for top performers in our aptitude quiz
- **Group discount** — 15% off when 3 or more people from the same organisation enrol together
Contact our admissions team to discuss the best option for you.

---

# Academy X FAQ - Career Support

## Q: What career support does Academy X provide?
A: Career support is built into every program:
- Dedicated career coach assigned to each trainee
- CV and LinkedIn profile review sessions
- Mock technical and behavioural interviews
- Access to our employer partner network (100+ companies)
- Job referral programme for graduates
- Alumni network and Slack community for ongoing networking
Our goal is to get you job-ready, not just certificate-ready.

## Q: What is your job placement rate?
A: Over 80% of our graduates secure a relevant tech role within 6 months of completing their program. We track outcomes for 12 months post-graduation to continuously improve our curriculum and employer partnerships.

## Q: What certificate will I receive upon completion?
A: Graduates receive a Academy X Certificate of Completion specific to their track. Our certificates are recognised by our employer partners. Additionally, we prepare you for industry-standard certifications such as AWS Certified Cloud Practitioner, CompTIA Security+, and Google Data Analytics Certificate.

---

# Academy X FAQ - Learning Experience

## Q: How are classes structured?
A: Each week includes:
- Live instruction sessions (2–3 times per week)
- Hands-on lab exercises and mini-projects
- Peer collaboration and code/design reviews
- Weekly 1-on-1 check-ins with your mentor
- A capstone project in the final weeks that you add to your portfolio

## Q: Who are the instructors?
A: All our instructors are active industry practitioners — software engineers, data scientists, and security professionals currently working at leading tech companies. They bring real-world problems into the classroom rather than purely academic content.

## Q: What happens if I fall behind or need extra help?
A: We have multiple support channels:
- Office hours with instructors three times a week
- A peer study group facilitated by a teaching assistant
- 24/7 access to recorded lessons and written notes
- A dedicated support chat channel on Slack
No trainee is left behind — we proactively reach out if we notice someone struggling.
"""


def get_sample_faqs():
    """Get sample FAQs as a list of documents."""
    return [SAMPLE_FAQS]
