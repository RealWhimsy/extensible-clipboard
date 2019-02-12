package org.libreoffice.example.clipboardapi;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

import org.json.simple.JSONObject;

public class RequestHandler {
	
	private URL serverUrl;
	private URL clipUrl;
	
	public RequestHandler(String baseUrl) throws MalformedURLException {
		updateServerUrl(baseUrl);
	}
	
	public void updateServerUrl(String baseUrl) throws MalformedURLException {
		serverUrl = new URL(baseUrl);
		clipUrl = new URL(baseUrl.concat("clip/"));
	}

	public JSONObject[] getAllClips() {
		return null;
	}
}
