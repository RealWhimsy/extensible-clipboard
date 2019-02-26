package org.libreoffice.example.clipboardapi;

import java.util.LinkedList;
import java.util.List;
import java.util.UUID;

import org.json.simple.JSONObject;

public class ClipEntry {

	private UUID _id;
	private String creationDate;
	private String mimetype;
	private String data;
	private byte[] bin_data;
	private String filename;
	private List<ClipEntry> children = new LinkedList<ClipEntry>();; 
	
	public ClipEntry(String uuid) {
		_id = UUID.fromString(uuid);
	}
	
	public ClipEntry(JSONObject json) {
		_id = UUID.fromString( ((String) json.get("_id")) );
	}
	
	public String getStringId() {
		return _id.toString();
	}
	
	public String getCreationDate() {
		return creationDate;
	}

	public void setCreationDate(String creationDate) {
		this.creationDate = creationDate;
	}

	public String getFilename() {
		return filename;
	}

	public void setFilename(String filename) {
		this.filename = filename;
	}

	public UUID getId() {
		return _id;
	}
	
	public String getMimetype() {
		return mimetype;
	}
	
	public void setMimetype(String mimetype) {
		this.mimetype = mimetype;
	}
	
	public String getData() {
		return data;
	}
	
	public byte[] getBinData() {
		return bin_data;
	}
	
	public void setBinData(byte[] bin_data) {
		this.bin_data = bin_data;
	}
	
	public void setData(Object data) {
		if (data instanceof String) {
			this.data = (String) data;
		} else {
			this.bin_data = (byte[]) data;
		}
	}
	
	public List<ClipEntry> getChildren() {
		return children;
	}
	
	public void addChild(ClipEntry child) {
		children.add(child);
	}
	
}
