package org.libreoffice.example.dialog;

import java.util.Collection;
import java.util.List;

import org.libreoffice.example.clipboardapi.ClipboardServer;
import org.libreoffice.example.clipboardapi.ClipEntry;
import org.libreoffice.example.helper.DialogHelper;

import com.sun.star.awt.XControl;
import com.sun.star.awt.XControlModel;
import com.sun.star.awt.tree.XMutableTreeDataModel;
import com.sun.star.awt.tree.XMutableTreeNode;
import com.sun.star.awt.tree.XTreeControl;
import com.sun.star.awt.tree.XTreeNode;
import com.sun.star.awt.XDialog;
import com.sun.star.awt.XDialogEventHandler;
import com.sun.star.beans.XPropertySet;
import com.sun.star.lang.WrappedTargetException;
import com.sun.star.uno.Any;
import com.sun.star.uno.Type;
import com.sun.star.uno.Exception;
import com.sun.star.uno.UnoRuntime;
import com.sun.star.uno.XComponentContext;
import com.sun.star.view.XSelectionSupplier;

public class ActionOneDialog implements XDialogEventHandler {

	private XComponentContext xContext;
	private XDialog dialog;
	private static final String actionOk = "actionOk";
	private static final String actionInsert = "actionInsert";
	private static final String actionSync = "actionSync";
	private String[] supportedActions = new String[] { actionOk, actionSync };
	private ClipboardServer cbServer;
	private Collection<ClipEntry> currentItems;

	public ActionOneDialog(XComponentContext xContext) throws Exception {
		this.xContext = xContext;
		this.dialog = DialogHelper.createDialog("ClipSelectDialog.xdl", this.xContext, this);
		testTree();
	}

	public void testTree() throws Exception{
		// https://forum.openoffice.org/en/forum/viewtopic.php?f=20&t=7348
		XControl tree = DialogHelper.getTree(this.dialog, "ClipTree");
		XControlModel model = tree.getModel();

		Object xTreeData = this.xContext.getServiceManager()
				.createInstanceWithContext("com.sun.star.awt.tree.MutableTreeDataModel", this.xContext);
		XMutableTreeDataModel mxTreeDataModel = (XMutableTreeDataModel) UnoRuntime
				.queryInterface(XMutableTreeDataModel.class, xTreeData);

		Type type = new Type(java.lang.String.class);
		Any any = new Any(type, "Clips");
		XMutableTreeNode root = mxTreeDataModel.createNode(any, true);
		any = new Any(type, "p1");
		XMutableTreeNode p1 = mxTreeDataModel.createNode(any, true);
		any = new Any(type, "p2");
		XMutableTreeNode p2 = mxTreeDataModel.createNode(any, true);
		any = new Any(type, "c1");
		XMutableTreeNode c1 = mxTreeDataModel.createNode(any, true);
		root.appendChild(p1);
		root.appendChild(p2);
		p2.appendChild(c1);
		
		mxTreeDataModel.setRoot(root);
		XPropertySet xTreeModelProperty = (XPropertySet) UnoRuntime.queryInterface(XPropertySet.class, model);
		xTreeModelProperty.setPropertyValue("DataModel", mxTreeDataModel);
	}


	public void fillTree() throws Exception {
		if ( currentItems == null ) {
			return;
		}
		// https://forum.openoffice.org/en/forum/viewtopic.php?f=20&t=7348
		XControl tree = DialogHelper.getTree(this.dialog, "ClipTree");
		XControlModel model = tree.getModel();

		Object xTreeData = this.xContext.getServiceManager()
				.createInstanceWithContext("com.sun.star.awt.tree.MutableTreeDataModel", this.xContext);
		XMutableTreeDataModel mxTreeDataModel = (XMutableTreeDataModel) UnoRuntime
				.queryInterface(XMutableTreeDataModel.class, xTreeData);

		XMutableTreeNode root = mxTreeDataModel.createNode("Clips", true);

		for (ClipEntry c : currentItems) {
			XMutableTreeNode parent = mxTreeDataModel.createNode(c.getData(), false);
			root.appendChild(parent);
			List<ClipEntry> children = c.getChildren();
			for (ClipEntry child : children) {
				XMutableTreeNode childNode = mxTreeDataModel.createNode(child.getData(), false);
				parent.appendChild(childNode);
			}
		}

		mxTreeDataModel.setRoot(root);
		XPropertySet xTreeModelProperty = (XPropertySet) UnoRuntime.queryInterface(XPropertySet.class, model);
		xTreeModelProperty.setPropertyValue("DataModel", mxTreeDataModel);
	}

	public void show() {
		dialog.execute();
	}

	private void onOkButtonPressed() {
		System.out.println("The girls are alright");
		dialog.endExecute();
	}

	private void onSyncButtonPressed() {
		String url = DialogHelper.getEditField(dialog, "ServerUrlInput").getText();
		if (cbServer == null) {
			cbServer = new ClipboardServer();
		}
		if (!cbServer.setServerURL(url)) {
			DialogHelper.showErrorMessage(xContext, dialog, "Invalid URL");
		}

		currentItems = cbServer.getAllClips();
		try {
			fillTree();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	private ClipEntry findEntry(String value) {
		for (ClipEntry curr : currentItems) {
			if (value.contains(curr.getData().toString())) {
				return curr;
			}
		}
		return null;
	}
	
	private void onInsertPressed() {
		XTreeControl xtreeControl = DialogHelper.getTreeControl(dialog, "ClipTree");
		XSelectionSupplier ss = (XSelectionSupplier) xtreeControl;
		Any selection = (Any) ss.getSelection();
		XTreeNode tn = (XTreeNode) selection.getObject();
		System.out.println(tn.getDisplayValue());
		DataInserter.insertIntoGUICursor(xContext,tn.getDisplayValue().toString());
		onOkButtonPressed();
		/*
		ClipEntry e = findEntry(tn.getDisplayValue().toString());
		if (e != null) {
			DataInserter.insertIntoGUICursor(e);
		}
		/*
		 * Create class to insert selected object
		 * > Get TextViewCursor
		 * > Insert Data
		 */
	}

	@Override
	public boolean callHandlerMethod(XDialog dialog, Object eventObject, String methodName)
			throws WrappedTargetException {
		if (methodName.equals(actionOk)) {
			onOkButtonPressed();
			return true; // Event was handled
		}
		if (methodName.equals(actionInsert)) {
			onInsertPressed();
			return true;
		}
		if (methodName.equals(actionSync)) {
			onSyncButtonPressed();
			return true;
		}
		return false; // Event was not handled
	}

	@Override
	public String[] getSupportedMethodNames() {
		return supportedActions;
	}

}
