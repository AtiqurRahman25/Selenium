"""
DMS-TC139
Chat with PDF
1. Upload a pdf file
2. Go to document details/full view page
3. Ask something
AI should provide proper response
"""
import os
import time

from selenium.webdriver.common.by import By

import common as c

TEST_CASE_ID = "DMS-TC139"

DOC_TYPE = os.getenv("OCR_DOC_TYPE", "/1 FC Test updated/OCR Test/")
QUESTION = "What is this document about?"


def chat(driver, wait):
    info = c.upload_document(driver, wait, "pdf", doc_type=DOC_TYPE)
    name = info["name"]
    c.open_document(driver, wait, name)
    time.sleep(2)

    # Locate Ask Effy chat input
    chat_box = driver.find_element(By.ID, "ai-chat")
    chat_box.clear()
    chat_box.send_keys(QUESTION)
    time.sleep(1)

    # Click Ask Effy submit button
    submit_btn = driver.find_element(By.ID, "ai-chat-submit")
    c.click(driver, submit_btn)

    # Wait for AI response in the scroll-bar conversation box
    end = time.time() + 60
    while time.time() < end:
        time.sleep(2)
        scroll_bars = driver.find_elements(By.ID, "scroll-bar")
        if scroll_bars:
            text = (scroll_bars[0].text or "").strip()
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            answers = [l for l in lines if l != QUESTION]
            if answers:
                full_ans = " ".join(answers)
                return True, f"AI answered: {full_ans[:120]}"

    return False, "no answer from the AI within 60 seconds"


SCENARIOS = [("Chat with PDF", chat)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
