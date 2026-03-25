"""Sample FAQ data for Company X."""

# Sample FAQs for testing and initial indexing
SAMPLE_FAQS = """
# Company X FAQ - Admissions

## Q: What are the admission requirements for undergraduate programs?
A: To apply for our undergraduate programs, you need:
- High school diploma or equivalent (GED)
- Minimum 2.5 GPA
- SAT score of 1000+ or ACT score of 20+
- Completed application form
- One letter of recommendation
- Personal essay (250-500 words)

## Q: What is the application deadline?
A: Application deadlines vary by program:
- Fall semester: June 30
- Spring semester: November 30
- Summer session: April 30

## Q: How much does tuition cost?
A: Our tuition rates for the academic year 2024-2025:
- Full-time undergraduate: $15,000 per semester
- Part-time undergraduate: $500 per credit hour
- Graduate programs: $12,000 per semester
Financial aid and scholarships are available.

## Q: Do you offer financial aid?
A: Yes, Company X offers various financial aid options:
- Merit-based scholarships
- Need-based grants
- Student loans
- Work-study programs
The Financial Aid Office can help you determine eligibility.

---

# Company X FAQ - Course Information

## Q: What is the average class size?
A: Our average undergraduate class size is 25-30 students. Introductory courses may have 50-100 students, while upper-level and graduate courses typically have 15-20 students.

## Q: Are online courses available?
A: Yes, Company X offers a variety of online courses. Most programs have a hybrid option combining in-person and online learning. Check the course catalog for specific offerings.

## Q: How many credits do I need to graduate?
A: Credit requirements depend on your degree:
- Associate degree: 60 credits
- Bachelor's degree: 120 credits
- Master's degree: 30-36 credits

## Q: Can I change my major?
A: Yes, you can change your major. Students typically have until the end of their sophomore year to declare or change their major without penalty. Contact your academic advisor for specific procedures.

---

# Company X FAQ - Student Services

## Q: How do I access the library?
A: The main library is open Monday-Friday 8AM-8PM and Saturday-Sunday 10AM-6PM. Your student ID gives you access to physical materials and online databases. Virtual reference services are available 24/7.

## Q: What health services are available?
A: Our Health Center offers:
- Primary care services
- Mental health counseling
- Immunizations and preventive care
- Emergency services
- Pharmacy services
All services are free for full-time students.

## Q: How do I find a roommate?
A: The Residential Life Office maintains a roommate matching service. You can complete a questionnaire to be matched with compatible roommates. Housing is guaranteed for first-year students.

## Q: What is the parking policy?
A: All students must register their vehicles. Parking permits cost $50 per semester for student lots. Metered parking is available near academic buildings. Overnight parking is prohibited on campus.

---

# Company X FAQ - Academic Support

## Q: Is tutoring available?
A: Yes, free tutoring is available through the Academic Success Center:
- One-on-one tutoring in all subjects
- Group study sessions
- Writing center services
- Math lab support
Appointments can be scheduled online.

## Q: How do I request academic accommodations?
A: Students with disabilities should contact the Disability Services Office. Accommodations may include:
- Extended test time
- Note-taking assistance
- Alternative testing formats
- Assistive technology access

## Q: What is the grading scale?
A: Our grading scale is:
- A: 90-100 (4.0)
- B: 80-89 (3.0)
- C: 70-79 (2.0)
- D: 60-69 (1.0)
- F: Below 60 (0.0)
The minimum passing grade is D.

## Q: How do I appeal a grade?
A: To appeal a grade, meet with the instructor within two weeks of receiving the grade. If unresolved, submit a formal appeal to the department chair with documentation.
"""


def get_sample_faqs():
    """Get sample FAQs as a list of documents."""
    return [SAMPLE_FAQS]
