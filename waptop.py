def installPackage(pkg_name):
	subprocess.call([sys.executable, '-m', 'pip', 'install', pkg_name])


browser = None
GROUP_NAME_XPATH = "//span[@title='2017 CSE CS909 WCN']"
RECENT_IMG_CLASS = "_1YbLB"
CAROUSEL_IMG_CLASS = "_2Ry6_"
SRC_IMG_CLASS = "_2-V0A"
CHROME_VER_WIN = 'wmic datafile where name="C:\\\\Program Files (x86)\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe" get Version /value'
CHROME_VER_UBU = 'google-chrome --version'
DRIVER_URL_UBU = 'https://chromedriver.storage.googleapis.com/__version__/chromedriver_linux64.zip'
DRIVER_URL_WIN = 'https://chromedriver.storage.googleapis.com/__version__/chromedriver_win32.zip'

def findElemByXpath(target):
	try:
		element = browser.find_element_by_xpath(target)
		return element
	except Exception as e:
		time.sleep(2)


def findElemByclass(target):
	try:
		element = browser.find_elements_by_class_name(target)
		return element
	except Exception as e:
		time.sleep(2)


def blob_downloader(url):
  result = browser.execute_async_script("""
    var uri = arguments[0];
    var callback = arguments[arguments.length - 1];
    var toBase64 = function(buffer) {
        for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)
            i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)
    };
    var xhr = new XMLHttpRequest();
    xhr.responseType = 'arraybuffer';
    xhr.onload = function(){ callback(toBase64(xhr.response)) };
    xhr.onerror = function(){ callback(xhr.status) };
    xhr.open('GET', uri);
    xhr.send();
    """, url)
  if type(result) == int :
    raise Exception("Request failed with status %s" %result)
  return base64.b64decode(result)


def downloader(url, filename, blob=False):
	if blob:
		blob_data = blob_downloader(url)
		with open("./temp_images/"+filename,'wb') as f:
			f.write(blob_data)
		return
	response = requests.get(url, stream = True)
	with open("./"+filename, 'wb') as f:
		for chunk in response.iter_content(chunk_size = 1024):
			if chunk:	
				f.write(chunk)


def chromeDriverDownloader():
	if sys.platform == 'linux':
		chrome_ver = os.popen("google-chrome --version").read().split()[2].split('.')[0]
		if chrome_ver:
			remote_ver =  requests.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE_' + chrome_ver).text
			downloader(DRIVER_URL_UBU.replace('__version__', remote_ver), 'chromedriver.zip')

	elif sys.platform == 'win32':
		chrome_ver = os.popen(CHROME_VER_WIN).read().strip().split('=')[1].split('.')[0]
		if chrome_ver:
			remote_ver = requests.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE_' + chrome_ver).text
			downloader(DRIVER_URL_WIN.replace('__version__', remote_ver), 'chromedriver.zip')

	with zipfile.ZipFile("chromedriver.zip", 'r') as zip:
		zip.extractall()
	if sys.platform == 'linux':
		os.chmod("./chromedriver", 0o777)


def initiateBrowser():
	
	print("[+] Initializing Browser...")
	
	chrome_options = Options()
	chrome_options.add_argument("--window-size=1920x1080")
	chrome_options.add_argument("user-data-dir=selenium")
	chrome_driver = os.getcwd() + "/chromedriver"
	if sys.platform == 'win32':
		chrome_driver += '.exe'
	global browser
	browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
	print("[+] Browser Ready. Scan the bar code if not done.")

def searchGroup():
	search_div = None
	while True:
		search_div = findElemByclass('_2S1VP')
		if search_div:
			search_div[0].click()
			search_div[0].send_keys('2017')
			break



def getImageList():
	print("[+] Searching WCN group...")
	browser.get('https://web.whatsapp.com')
	searchGroup()
	while True:
		group_element = findElemByXpath(GROUP_NAME_XPATH)
		if group_element:
			group_element.click()
			break

	print("[+] WhatsApp  group found.")
	print("[+] Searching the image collection...")
	while True:
		image_element = findElemByclass(RECENT_IMG_CLASS)
		if image_element:
			time.sleep(3)
			image_element[-1].click()
			break	
	time.sleep(2)
	image_list = findElemByclass(CAROUSEL_IMG_CLASS)
	first_img_element = None
	while image_list[0] != first_img_element:
		first_img_element = image_list[0]
		image_list[0].click()
		image_list = findElemByclass(CAROUSEL_IMG_CLASS)

	print("[+] Image collection found.")
	return image_list
	

def imageDownloadLoop(image_list):
	print("[+] Downloading images...")
	try:
		os.mkdir("temp_images")
	except Exception as e:
		pass
	
	progress = progressbar.ProgressBar(maxval=len(image_list), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	progress.start()
	for i in  range(1, len(image_list)+1):
		try:
			image_list[i-1].click()
			while True:
				retry_flag = 0
				while retry_flag != 20:
					clicked_img = findElemByclass(SRC_IMG_CLASS)
					retry_flag += 1
				if clicked_img:
					break
				if retry_flag == 20:
					break
			img_src = clicked_img[0].get_attribute("src")
			filename = "image_" + str(i) +".jpeg"
			downloader(img_src, filename, True)
			progress.update(i)
		except Exception as e:
			print("")
		
	progress.finish()
	return [os.getcwd() + '/temp_images/image_' + str(i) + ".jpeg" for i in range(1,len(image_list)+1)]


def pdf_generator(image_list):
	print("[+] Images Downloaded.")
	print("[+] Generating PDF...")
	with open("2017_CSE_CS909_WCN.pdf", "wb") as f:
		f.write(img2pdf.convert(image_list))
	print("[+] Your PDF file is ready for use. Thank you for using this software.")


def purgeUselessFiles():
	shutil.rmtree(os.getcwd()+ "/temp_images")
	os.remove('./chromedriver.zip')
	if sys.platform == 'win32':
		os.remove('./chromedriver.exe')
	elif sys.platform == 'linux':
		os.remove('./chromedriver')


def main():
	chromeDriverDownloader()
	initiateBrowser()
	image_list = getImageList()
	file_names = imageDownloadLoop(image_list)
	pdf_generator(file_names)
	browser.quit()
	purgeUselessFiles()


if __name__ == '__main__':
	print("© Developed By Anand\n")
	print("[+] Checing for the required python libraries...")
	library_flag = 0
	PACKAGES = ['subprocess','sys','selenium', 'time','zipfile','os','base64','shutil','progressbar','requests', 'img2pdf']
	for package in PACKAGES:
		exec(f'global {package}')
		try:
			exec(f'{package} = __import__(package)')
		except Exception as e:
			library_flag  = 1
			print(f'[+] {package} not found. Installing...')
			installPackage(package)
		finally:
			exec(f'{package} = __import__(package)')
	from selenium.webdriver.chrome.options import Options
	from selenium import webdriver
	if library_flag:
		print("[+] All the required python libraries are installed.")
	else:
		print("[+] Library requirement is already fulfilled.")
	main()
