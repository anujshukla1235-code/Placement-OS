import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User, CompanyProfile, CollegeProfile
from students.models import StudentProfile
from jobs.models import Job, Application
from interviews.models import Interview


class Command(BaseCommand):
    help = "Seed realistic enterprise demo data for Placement OS demonstration, or clear with --clear"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear previously created demo accounts, jobs, and interviews",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing demo records...")
            demo_emails = [
                "tpo@placement.edu",
                "recruiter@google.com",
                "recruiter@microsoft.com",
                "recruiter@amazon.com",
                "director@iit.edu",
                "student@placement.edu",
            ]
            User.objects.filter(email__in=demo_emails).delete()
            self.stdout.write(self.style.SUCCESS("Successfully cleared demo data."))
            return

        self.stdout.write("Seeding realistic enterprise demo data...")

        # 1. TPO / Super Admin
        tpo_user, _ = User.objects.get_or_create(
            email="tpo@placement.edu",
            defaults={
                "first_name": "TPO",
                "last_name": "Head",
                "role": "ADMIN",
                "is_verified": True,
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        tpo_user.set_password("Admin@123")
        tpo_user.save()

        # 2. College / University
        college_user, _ = User.objects.get_or_create(
            email="director@iit.edu",
            defaults={
                "first_name": "Campus",
                "last_name": "Director",
                "role": "COLLEGE",
                "is_verified": True,
                "is_active": True,
            },
        )
        college_user.set_password("College@123")
        college_user.save()

        college_profile, _ = CollegeProfile.objects.get_or_create(
            user=college_user,
            defaults={
                "college_name": "Indian Institute of Technology (Main Campus)",
                "tpo_name": "Dr. Rajesh Verma",
                "tpo_phone": "+919876543210",
                "is_approved": True,
            },
        )

        # 3. Companies
        companies_data = [
            {
                "email": "recruiter@google.com",
                "name": "Google India",
                "hr": "Sundar HR",
                "website": "https://google.com",
                "job": {
                    "title": "Software Development Engineer (L3)",
                    "description": "Join Google as an SDE. Work on large scale distributed cloud infrastructure, microservices, and modern web architectures.",
                    "skills_required": "Data Structures, Algorithms, Python, Go, Distributed Systems",
                    "eligibility_branch": ["CSE", "IT", "ECE"],
                    "min_cgpa": 7.5,
                    "ctc": "28 LPA",
                    "location": "Bengaluru",
                },
            },
            {
                "email": "recruiter@microsoft.com",
                "name": "Microsoft IDC",
                "hr": "Satya HR",
                "website": "https://microsoft.com",
                "job": {
                    "title": "Frontend Software Engineer",
                    "description": "Build high performance user interfaces for Microsoft 365, Azure Portal, and developer productivity suites.",
                    "skills_required": "React, TypeScript, Next.js, Web Performance, Tailwind CSS",
                    "eligibility_branch": ["CSE", "IT"],
                    "min_cgpa": 7.0,
                    "ctc": "24 LPA",
                    "location": "Hyderabad",
                },
            },
            {
                "email": "recruiter@amazon.com",
                "name": "Amazon Web Services (AWS)",
                "hr": "Andy HR",
                "website": "https://amazon.com",
                "job": {
                    "title": "Cloud Support Associate",
                    "description": "Collaborate with global AWS enterprise clients to diagnose, troubleshoot, and optimize cloud architectures.",
                    "skills_required": "Linux, Networking, Cloud Architecture, Python, Docker",
                    "eligibility_branch": ["CSE", "IT", "ECE", "MECH"],
                    "min_cgpa": 6.5,
                    "ctc": "18 LPA",
                    "location": "Pune",
                },
            },
        ]

        created_jobs = []
        for comp in companies_data:
            c_user, _ = User.objects.get_or_create(
                email=comp["email"],
                defaults={
                    "first_name": comp["hr"].split()[0],
                    "last_name": comp["hr"].split()[-1],
                    "role": "COMPANY",
                    "is_verified": True,
                    "is_active": True,
                },
            )
            c_user.set_password("Company@123")
            c_user.save()

            c_prof, _ = CompanyProfile.objects.get_or_create(
                user=c_user,
                defaults={
                    "company_name": comp["name"],
                    "hr_name": comp["hr"],
                    "website": comp["website"],
                    "is_approved": True,
                },
            )

            job_info = comp["job"]
            job, _ = Job.objects.get_or_create(
                company=c_prof,
                title=job_info["title"],
                defaults={
                    "description": job_info["description"],
                    "skills_required": job_info["skills_required"],
                    "eligibility_branch": job_info["eligibility_branch"],
                    "min_cgpa": job_info["min_cgpa"],
                    "ctc": job_info["ctc"],
                    "location": job_info["location"],
                    "is_active": True,
                    "status": "OPEN",
                },
            )
            created_jobs.append(job)

        # 4. Student Demo Account
        student_user, _ = User.objects.get_or_create(
            email="student@placement.edu",
            defaults={
                "first_name": "Aman",
                "last_name": "Sharma",
                "role": "STUDENT",
                "is_verified": True,
                "is_active": True,
            },
        )
        student_user.set_password("Student@123")
        student_user.save()

        student_prof, _ = StudentProfile.objects.get_or_create(
            user=student_user,
            defaults={
                "college": college_profile,
                "enrollment_number": "2024CSE001",
                "branch": "CSE",
                "course": "B.Tech",
                "semester": 8,
                "cgpa": 8.85,
                "is_verified": True,
                "skills": ["React", "Python", "SQL", "Data Structures"],
            },
        )

        # 5. Demo Applications
        if len(created_jobs) >= 2:
            # Application 1: Google (Shortlisted / Interview)
            app1, _ = Application.objects.get_or_create(
                job=created_jobs[0],
                student=student_prof,
                defaults={
                    "status": "INTERVIEW",
                    "ats_score": 92.0,
                },
            )

            # Application 2: Microsoft (Applied)
            app2, _ = Application.objects.get_or_create(
                job=created_jobs[1],
                student=student_prof,
                defaults={
                    "status": "APPLIED",
                    "ats_score": 86.5,
                },
            )

            # 6. Scheduled Interview for Google
            interview_time = timezone.now() + datetime.timedelta(days=2, hours=3)
            Interview.objects.get_or_create(
                application=app1,
                defaults={
                    "scheduled_at": interview_time,
                    "mode": "ONLINE (Google Meet)",
                    "panel_details": "Google Senior Engineering Panel",
                    "status": "Scheduled",
                },
            )

        self.stdout.write(self.style.SUCCESS("\n--- Demo Data Seeding Complete! ---"))
        self.stdout.write("Test Accounts Created:")
        self.stdout.write("  Student: student@placement.edu / Student@123 (Aman Sharma, CSE, 8.85 CGPA)")
        self.stdout.write("  TPO:     tpo@placement.edu / Admin@123 (Admin Panel & Approvals)")
        self.stdout.write("  Company: recruiter@google.com / Company@123 (Google India)")
        self.stdout.write("  Company: recruiter@microsoft.com / Company@123 (Microsoft IDC)")
        self.stdout.write("  College: director@iit.edu / College@123 (Campus Dashboard)")
        self.stdout.write("Active Openings: Google (28 LPA), Microsoft (24 LPA), Amazon (18 LPA)")
        self.stdout.write("Applications & Interviews: 2 submitted applications, 1 scheduled online interview.\n")
