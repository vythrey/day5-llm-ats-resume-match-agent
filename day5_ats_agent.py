import json
import re
import ollama


class MemoryAgent:
    def __init__(self):
        self.memory = {}

    def store(self, key, value):
        self.memory[key] = value

    def recall(self, key):
        return self.memory.get(key, "No memory found.")


class LLMATSResumeMatchAgent:
    def __init__(self, model_name="llama3.2:1b"):
        self.memory = MemoryAgent()
        self.model_name = model_name

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s\+\#\.]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def extract_json_from_response(self, response_text):
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1

            if start != -1 and end != -1:
                json_text = response_text[start:end]
                return json.loads(json_text)

            raise ValueError("Could not extract valid JSON from LLM response.")

    def extract_important_requirements(self, job_description):
        prompt = f"""
You are an ATS resume analysis assistant.

Task:
Read the job description and extract only important resume-matching requirements.

Do NOT include generic words like:
good, nice, candidate, team player, motivated, fast-paced, company, role, job.

Extract items that matter for matching a resume:
- technical skills
- tools/software/platforms
- business skills
- responsibilities
- qualifications/certifications

Return ONLY valid JSON in this exact format:
{{
  "technical_skills": [],
  "tools": [],
  "business_skills": [],
  "responsibilities": [],
  "qualifications": []
}}

Job Description:
{job_description}
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response["message"]["content"].strip()
        return self.extract_json_from_response(content)

    def flatten_requirements(self, requirements):
        weighted_items = []

        category_weights = {
            "technical_skills": 3,
            "tools": 3,
            "business_skills": 2,
            "responsibilities": 2,
            "qualifications": 2
        }

        for category, weight in category_weights.items():
            items = requirements.get(category, [])

            for item in items:
                if isinstance(item, str) and item.strip():
                    weighted_items.append({
                        "category": category,
                        "item": item.strip(),
                        "weight": weight
                    })

        return weighted_items

    def item_matches_resume(self, item, resume_text):
        item_clean = self.clean_text(item)
        resume_clean = self.clean_text(resume_text)

        if item_clean in resume_clean:
            return True

        item_words = item_clean.split()

        if len(item_words) == 1:
            return item_words[0] in resume_clean.split()

        matched_words = 0

        for word in item_words:
            if len(word) > 2 and word in resume_clean:
                matched_words += 1

        match_ratio = matched_words / len(item_words)

        return match_ratio >= 0.7

    def calculate_score(self, weighted_items, resume_text):
        if not weighted_items:
            return 0, [], []

        total_weight = 0
        matched_weight = 0
        matched_items = []
        missing_items = []

        for entry in weighted_items:
            item = entry["item"]
            weight = entry["weight"]
            category = entry["category"]

            total_weight += weight

            if self.item_matches_resume(item, resume_text):
                matched_weight += weight
                matched_items.append(entry)
            else:
                missing_items.append(entry)

        score = (matched_weight / total_weight) * 100
        return round(score, 2), matched_items, missing_items

    def generate_report(self, job_description, resume_text):
        requirements = self.extract_important_requirements(job_description)
        weighted_items = self.flatten_requirements(requirements)

        score, matched_items, missing_items = self.calculate_score(
            weighted_items,
            resume_text
        )

        self.memory.store("last_score", score)
        self.memory.store("last_requirements", requirements)
        self.memory.store("last_matched_items", matched_items)
        self.memory.store("last_missing_items", missing_items)

        report = "\nATS-Style Resume Match Report\n"
        report += "=" * 40 + "\n\n"

        report += f"Estimated Keyword Alignment Score: {score}%\n\n"

        report += "Important Requirements Extracted:\n"
        for category, items in requirements.items():
            report += f"\n{category.replace('_', ' ').title()}:\n"
            if items:
                for item in items:
                    report += f"- {item}\n"
            else:
                report += "- None found\n"

        report += "\nMatched Requirements:\n"
        if matched_items:
            for entry in matched_items:
                report += f"- [{entry['category']}] {entry['item']}\n"
        else:
            report += "- No important requirements matched\n"

        report += "\nMissing / Weakly Matched Requirements:\n"
        if missing_items:
            for entry in missing_items:
                report += f"- [{entry['category']}] {entry['item']}\n"
        else:
            report += "- No major gaps found\n"

        report += "\nTruthful Resume Improvement Suggestions:\n"

        if missing_items:
            missing_terms = []

            for entry in missing_items:
                cleaned_item = entry["item"].replace("_", " ")
                missing_terms.append(cleaned_item)

            unique_missing_terms = sorted(set(missing_terms))

            report += "Missing or weak areas to review:\n"
            report += "- " + ", ".join(unique_missing_terms) + "\n\n"
            report += (
                "If these reflect your real experience, consider adding them naturally "
                "into your resume bullets. Do not add anything you have not actually done.\n"
            )
        else:
            report += "- Resume appears well aligned with the extracted requirements.\n"

        report += "\nImportant Note:\n"
        report += (
            "This is not a real ATS score. It is an estimated keyword alignment "
            "score based on extracted job requirements and resume text matching.\n"
        )

        return report


if __name__ == "__main__":
    agent = LLMATSResumeMatchAgent()

    print("LLM-Based ATS Resume Match Agent is running.\n")

    print("Paste the job description below.")
    print("When finished, type END on a new line.\n")

    jd_lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        jd_lines.append(line)

    job_description = "\n".join(jd_lines)

    print("\nPaste your resume below.")
    print("When finished, type END on a new line.\n")

    resume_lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        resume_lines.append(line)

    resume_text = "\n".join(resume_lines)

    try:
        report = agent.generate_report(job_description, resume_text)
        print("\n" + report)
    except Exception as error:
        print("\nSomething went wrong.")
        print("Error details:")
        print(error)
        print("\nTroubleshooting tips:")
        print("- Make sure Ollama is running: ollama serve")
        print("- Make sure the model is downloaded: ollama pull llama3.2:1b")
        print("- Try running again. Small local models may sometimes return invalid JSON.")