package org.libreoffice.example.clipboardapi;

import java.util.Date;
import java.util.LinkedList;
import java.util.List;
import java.util.UUID;

import org.json.simple.JSONObject;

public class ClipEntry {

	private UUID _id;
	private Date creationDate;
	private String mimetype;
	private Object data;
	private String filename;
	private List<ClipEntry> children = new LinkedList<ClipEntry>();
	
	public ClipEntry(String uuid) {
		_id = UUID.fromString(uuid);
	}
	
	public ClipEntry(JSONObject json) {
		_id = UUID.fromString( ((String) json.get("_id")) );
	}
	
	public Date getCreationDate() {
		return creationDate;
	}

	public void setCreationDate(Date creationDate) {
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
	
	public Object getData() {
		return data;
	}
	
	public void setData(Object data) {
		this.data = data;
	}
	
	public List<ClipEntry> getChildren() {
		return children;
	}
	
	public void addChild(ClipEntry child) {
		children.add(child);
	}
	
}
