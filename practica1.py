#!/usr/bin/python
#Daniel Rubio Villegas

import webapp
import socket
import urllib.parse
import csv

def formulario(msg):

	htmlAnswer = "<html><head><title>"
	htmlAnswer += "Acortador URL's</title></head>"
	htmlAnswer += "<body><p><h5>" + str(msg) + "</h5></p>"
	htmlAnswer += "<form id='formulario' action='' method='POST'>"
	htmlAnswer += "<fieldset><legend><b style= 'color:blue'>Acortador de url's</b></legend>"
	htmlAnswer += "<label>URL: </label>"
	htmlAnswer += "<input type='text' name='url' value=''/>"
	htmlAnswer += "<input type='submit' value='Send It!' /></fieldset></form>"
	htmlAnswer += "</body></html>"

	return htmlAnswer

class contentApp(webapp.webApp):

	dicc_id_url = {}
	dicc_id_cut = {}
	idn = 0

	def parse(self, request):
		metodo = request.split()[0]
		print(chr(27) + "[0;33m" + "METODO_RCV: " + str(metodo) + chr(27) + "[0m")
		recurso = request.split()[1]
		print(chr(27) + "[0;33m" + "RECURSO_RCV: " + str(recurso) + chr(27) + "[0m")

		if metodo == 'POST':
			request_list = request.split()
			request_url = request_list[31]
			url = request_url.split('=')[1]
			url = urllib.parse.unquote(url,'utf-8', 'replace')
			print(chr(27) + "[0;33m" + "URL_RCV: " + str(url) + chr(27) + "[0m\n")
		else:
			print("")
			url = None

		return (metodo, recurso, url)

	def process (self, parsedRequest):
		(metodo, recurso, url) = parsedRequest

		if recurso == '/' and metodo == 'GET':
			msg = ''
			htmlAnswer = formulario(msg)
			htmlAnswer += "<html><head><body>"

			if self.idn != 0:
				htmlAnswer += '<p><h3>''\n\nLista urls enteras-->recortadas''</h3></p>'
				htmlAnswer += '<p>''------------------------------------------------------------------''</p>'
				for Id in self.dicc_id_url:
					url_normal = self.dicc_id_url[Id]
					url_acortada = 'http://localhost:1234/' + str(Id)
					htmlAnswer += '<p>' + str(url_normal[0]) +  ' ==Id acortada=> '
					htmlAnswer += str(url_acortada) + '</p>'

			returnCode = "200 OK"

		else:
			recurso = recurso.split('/')[1]

			if recurso != '/' and metodo == 'GET':
				recurso_num = True

				try:
					recurso = int(recurso)
				except ValueError:
					recurso_num = False
					print ('Me han ingresado un recurso que no es un numero: ' + str(recurso))

				if recurso in self.dicc_id_cut:
					url_cut_rcv = self.dicc_id_cut[recurso] #Es la url que recibo por get acortada, y extraigo la url normal del dicc
					url_real = self.dicc_id_url[recurso][0]
					print("REDIRECCIONANDO A: " + str(url_real))
					htmlAnswer = "<html><head><body>"
					htmlAnswer += "<p><h5>"'Estas siendo redirigido a: '+ str(url_real) + "</h5></p>"
					htmlAnswer += "Redirecting... <meta http-equiv='refresh' content='2;"
					htmlAnswer += "URL="
					htmlAnswer += str(url_real)
					htmlAnswer += "'></p>"
					htmlAnswer += "</body></head></html>"
					returnCode = "308 Permanent Redirect " + str(url_real)
				else:
					if not recurso_num:
						msg = 'HTTP 400 Bad Request. El recurso no es valido'
						returnCode = "400 Bad Request"
						htmlAnswer = formulario(msg)

					else:
						msg = 'HTTP 404 Not Found. Recurso no disponible.'
						returnCode = "404 Not Found"
						htmlAnswer = formulario(msg)

					print (chr(27) + "[0;31m" + "ERROR: " + str(msg) + chr(27) + "[0m\n")


			if metodo == 'POST':
				url_http = url[0:7]
				url_https = url[0:8]
				print("HTTP: " + str(url_http))
				print("HTTPS: " + str(url_https))
				haveIt = False
				http = False
				https = False

				if url_http == 'http://':
					http = True
					print("HTTP TRUE")
				elif url_https == 'https://':
					https = True
					print("HTTPS TRUE")

				for ID in self.dicc_id_url:
					url_deldicc = self.dicc_id_url[ID][0]

					print ("url_diccionario: " + str(url_deldicc))
					if http:
						url_comp_value = str(url)
						#print ("url_comp: " + str(url_comp_value))
					elif https:
						url = 'http://' + url[8:]
						url_comp_value = str(url)
					else:
						url_comp_value = "http://" + str(url)
						print ("url_comp: " + str(url_comp_value))

					if str(url_comp_value) == str(url_deldicc):
						#print("IS IN: " + str(ID))
						haveIt = True
						returnCode = "418 I'm a teapot"
						url_cut = self.dicc_id_cut[ID]
						url_cut = url_cut[0]
						url_real = self.dicc_id_url[ID]
						url_real = url_real[0]
						#print ("URL_CUT" + str(url_cut))
						#print ("URL_REAL" + str(url_real))
						htmlAnswer = "<html><body><p><h3><font color = 'red'> Url ya ingresada.</font></h3></p>"
						htmlAnswer += "<p>Url acortada: <a href=" + url_cut + ">" + url_cut + "</a></p>"
						htmlAnswer += "<p>Url ingresada: <a href=" + url_real + ">" + url_real + "</a></p>"
						htmlAnswer += "</body></html>"
						msg = "<p>Puedes acortar otra url :)</p>"
						htmlAnswer += formulario(msg)
				
				if not haveIt: # Creo nueva url
					urlcut = 'http://localhost:1234/' + str(self.idn)
					self.dicc_id_cut[self.idn] = [urlcut]
					returnCode = "200 OK"
					msg = "Nueva url acortada: " + str(urlcut)

					if http:
						self.dicc_id_url[self.idn] = [url]
						#print("1")
					elif https:
						url = 'http://' + url[8:]
						self.dicc_id_url[self.idn] = [url]
						#print("2")
					else:
						url = "http://" + str(url)
						self.dicc_id_url[self.idn] = [url]
						#print("3")

					self.idn = self.idn + 1
					htmlAnswer = formulario(msg)

		print (str(self.dicc_id_url) , str(self.dicc_id_cut))
		return (returnCode, htmlAnswer)


if __name__ == "__main__":
    testWebApp = contentApp("localhost", 1234)
