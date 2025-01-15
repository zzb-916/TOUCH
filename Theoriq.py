import time

from selenium import webdriver



        # 设置 ChromeDriver 的路径（请根据实际路径更新）
        chromedriver_path = r'D:\chromedriver-win64\chromedriver.exe'  # 替换为你的 chromedriver 路径
        service = Service(executable_path=chromedriver_path)

        # 使用指定路径初始化 WebDriver
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"An error occurred while initializing the driver: {e}")
        return None

def open_website(driver):
    try:
        # 打开网页
        driver.get('https://infinity.theoriq.ai/studio/chat')
        print("Page title is: " + driver.title)
    except Exception as e:
        print(f"An error occurred while opening the website: {e}")

def main():
    driver = initialize_driver()  # 初始化 WebDriver

    if driver:
        try:
            open_website(driver)  # 打开网页并打印页面标题
            time.sleep(10)
        finally:
            time.sleep(10)  # 无论如何都关闭浏览器
    else:
        print("Failed to initialize the driver.")

if __name__ == '__main__':
    main()
