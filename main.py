import random
import time

from g4f.client import Client
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

with open('username.txt', 'r', encoding='utf-8') as file:
    usernames = file.readlines()

code = input("Enter code: ")
num_bots = int(input("Enter number of bots: "))

drivers = []


def generate_question(question):
    template = f"""
    Вопрос: {question}
    Представь, что ты играешь в игру с вопросами. Твоя задача — придумать максимально смешной и остроумный ответ, 
    используя такие темы, как сперма, Стас наш друг даун который показал свой член, гирба наш однокласник который смотрит
    шкибиди туалеты, бальба нащ учитель по матиматики, Гитлер и тому подобное. 
    Твой ответ должен быть не больше одного предложения и быть 25 символов максимально и ты должен генерируть только
    один вариант и без "Ответ: ", "Ваш Ответ: ", просто что ты придумал пиши просто и можешь писать с ошибками
    """
    client = Client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": template}]
    )
    answer = response.choices[0].message.content or ""
    print(f"Generated answer: {answer}")
    return answer


def create_driver_instance():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get('https://jackbox.fun/')
    return driver


def check_elements(driver):
    try:
        wait = WebDriverWait(driver, 20)
        submit_button = wait.until(EC.visibility_of_element_located((By.ID, "quiplash-submit-answer")))
        answer_input = wait.until(EC.visibility_of_element_located((By.ID, "quiplash-answer-input")))
        print("Submit button and answer input are visible.")
        return submit_button.is_displayed() and answer_input.is_displayed()
    except NoSuchElementException as e:
        print(f"Element not found: {e}")
        return False
    except TimeoutException as e:
        print(f"Timeout: {e}")
        return False


def answer_question(driver, question):
    try:
        question_input = driver.find_element(By.ID, "quiplash-answer-input")
        question_input.send_keys(generate_question(question))
        submit_button = driver.find_element(By.ID, "quiplash-submit-answer")
        submit_button.click()
    except Exception as e:
        print(f"Error answering question: {e}")


for _ in range(num_bots):
    driver = create_driver_instance()
    drivers.append(driver)

    username = random.choice(usernames).strip()
    roomcodeSearch = driver.find_element(By.ID, "roomcode")
    usernameSearch = driver.find_element(By.ID, "username")

    roomcodeSearch.send_keys(code)
    usernameSearch.send_keys(username)

    buttonJoinSearch = driver.find_element(By.ID, "button-join")
    time.sleep(2)
    buttonJoinSearch.click()

while True:
    all_elements_found = True
    for driver in drivers:
        if not check_elements(driver):
            all_elements_found = False
            print("Элементы не найдены. Проверка через 5 секунд...")
            break

    if all_elements_found:
        print("Элементы найдены, отправляю ответ...")
        for driver in drivers:
            try:
                question = driver.find_element(By.XPATH, "//p[@id='question-text']").text
                print(question)
                answer_question(driver, question)
            except NoSuchElementException:
                print("Не удалось найти вопрос.")

    time.sleep(5)