package org.libreoffice.example.clipboardapi;

import java.net.MalformedURLException;
import java.util.Collections;
import java.util.List;
import org.json.simple.JSONObject;

public class ClipboardServer {
	
	private RequestHandler rqHandler;

	public boolean setServerURL(String baseUrl) {
		try {
			if ( rqHandler == null) {
				rqHandler = new RequestHandler(baseUrl);
			}
			else {
				rqHandler.updateServerUrl(baseUrl);
			}
			return true;
		} catch (MalformedURLException e) {
			return false;
		}
	}
	
	public List<ClipEntry> getAllClips() {
		JSONObject[] clips = rqHandler.getAllClips();
		// Make hashmap with _id as key & ClipEntry as value
		// if parent -> add as child
		// else map[key] == null: enter
		// needs to be sorted by creation-date
		return null;
	}
}
