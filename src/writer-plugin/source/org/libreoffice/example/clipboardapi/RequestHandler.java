package org.libreoffice.example.clipboardapi;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class RequestHandler {
	
	private JSONParser parser;
	private URL serverUrl;
	private URL clipUrl;
	
	public RequestHandler(String baseUrl) throws MalformedURLException {
		updateServerUrl(baseUrl);
		parser = new JSONParser();
	}
	
	public void updateServerUrl(String baseUrl) throws MalformedURLException {
		serverUrl = new URL(baseUrl);
		clipUrl = new URL(baseUrl.concat("clip/"));
	}
	
	private String buildStringFromConnection(HttpURLConnection conn) throws IOException{
		InputStream in = conn.getInputStream();
		BufferedReader br = new BufferedReader( new InputStreamReader(in) );
		StringBuilder response = new StringBuilder();
		String line;
		line = br.readLine();
		while ( line != null ) {
			response.append(line);
			response.append("\n");
			line = br.readLine();
		}
		br.close();
		return response.toString();

	}

	public JSONArray getAllClips() {
		JSONArray json = new JSONArray();
		try {
			HttpURLConnection conn = (HttpURLConnection) clipUrl.openConnection();
			conn.setRequestProperty("Contenty-Type", "application/json");
			conn.setInstanceFollowRedirects(true);
			conn.setConnectTimeout(3000);
			
			String result = buildStringFromConnection(conn);
			json = (JSONArray) parser.parse(result);
			
			
		} catch (IOException e) {
			e.printStackTrace();
		} catch (ParseException e) {
			e.printStackTrace();
		}
		return json;
	}
	
	public boolean sendStringToServer(JSONObject toSend) {
		try {
			HttpURLConnection conn = (HttpURLConnection) clipUrl.openConnection();
			conn.setRequestMethod("POST");
			conn.setRequestProperty("Contenty-Type", "application/json");
			conn.setInstanceFollowRedirects(true);
			conn.setConnectTimeout(3000);
			
			OutputStreamWriter wr= new OutputStreamWriter(conn.getOutputStream());
			wr.write(toSend.toString());
			wr.close();
			
			if (conn.getResponseCode() == 201) {
				return true;
			}
			
		} catch (Exception e) {
			return false;
		}
		return false; // no 201
	}
}
