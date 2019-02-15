package org.libreoffice.example.comp;

import com.sun.star.uno.AnyConverter;
import com.sun.star.uno.Exception;
import com.sun.star.uno.UnoRuntime;
import com.sun.star.uno.XComponentContext;
import com.sun.star.util.XChangesBatch;
import com.sun.star.lib.uno.helper.Factory;

import org.libreoffice.example.clipboardapi.ClipboardServer;
import org.libreoffice.example.dialog.ActionOneDialog;
import org.libreoffice.example.helper.DialogHelper;
import org.libreoffice.example.options.ConfigurationAccess;

import com.sun.star.awt.XControl;
import com.sun.star.awt.XControlContainer;
import com.sun.star.awt.XWindow;
import com.sun.star.beans.XPropertySet;
import com.sun.star.container.XNameAccess;
import com.sun.star.lang.WrappedTargetException;
import com.sun.star.lang.XSingleComponentFactory;
import com.sun.star.registry.XRegistryKey;
import com.sun.star.lib.uno.helper.WeakBase;

public final class StarterProjectImpl extends WeakBase implements com.sun.star.awt.XContainerWindowEventHandler,
		com.sun.star.lang.XServiceInfo, com.sun.star.task.XJobExecutor {
	private ActionOneDialog actionOneDialog;
	private final XComponentContext m_xContext;
	private static ClipboardServer cbServer = new ClipboardServer();
	private static final String m_implementationName = StarterProjectImpl.class.getName();
	private static final String[] m_serviceNames = { "org.libreoffice.example.StarterProject" };
	private static final String[] m_controlNames = { "txtUrl" };
	private XNameAccess accessLeaves;

	public StarterProjectImpl(XComponentContext context) {
		m_xContext = context;

		 accessLeaves = ConfigurationAccess.createUpdateAccess( 
				 context,
				 "/org.openoffice.Office.OptionsPageDemo/Leaves" 
		);
		 
	};

	public static XSingleComponentFactory __getComponentFactory(String sImplementationName) {
		XSingleComponentFactory xFactory = null;

		if (sImplementationName.equals(m_implementationName))
			xFactory = Factory.createComponentFactory(StarterProjectImpl.class, m_serviceNames);
		return xFactory;
	}

	public static boolean __writeRegistryServiceInfo(XRegistryKey xRegistryKey) {
		return Factory.writeRegistryServiceInfo(m_implementationName, m_serviceNames, xRegistryKey);
	}

	// com.sun.star.lang.XServiceInfo:
	public String getImplementationName() {
		return m_implementationName;
	}

	public boolean supportsService(String sService) {
		int len = m_serviceNames.length;

		for (int i = 0; i < len; i++) {
			if (sService.equals(m_serviceNames[i]))
				return true;
		}
		return false;
	}

	public String[] getSupportedServiceNames() {
		return m_serviceNames;
	}

	// com.sun.star.task.XJobExecutor:
	public void trigger(String action) {
		if (cbServer == null) {
			/*
			 * Intended to cache entries here but after closing the dialog the whole
			 * this-object seems to get deleted
			 */
			System.out.println("Creating new server");
			cbServer = new ClipboardServer();
		}
		switch (action) {
		case "insert":
			System.out.println("inserting");
			try {
				if (actionOneDialog == null) {
					actionOneDialog = new ActionOneDialog(m_xContext, cbServer);
				}
				actionOneDialog.show();
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			break;
		case "copy":
			System.out.println("copying");
			break;
		default:
			DialogHelper.showErrorMessage(m_xContext, null, "Unknown action: " + action);
		}

	}

	@Override
	public boolean callHandlerMethod(XWindow aWindow, Object aEventObject, String sMethod)
			throws WrappedTargetException {
		if (sMethod.equals("external_event")) {
			try {
				return handleExternalEvent(aWindow, aEventObject);
			} catch (com.sun.star.uno.RuntimeException re) {
				throw re;
			} catch (com.sun.star.uno.Exception e) {
				e.printStackTrace();
				throw new WrappedTargetException(sMethod, this, e);
			}
		}
		// return false when event was not handled
		return false;
	}

	private boolean handleExternalEvent(XWindow aWindow, Object aEventObject) throws com.sun.star.uno.Exception {
		try {
			String sMethod = AnyConverter.toString(aEventObject);
			if (sMethod.equals("ok")) {
				saveData(aWindow);
			} else if (sMethod.equals("back") || sMethod.equals("initialize")) {
				loadData(aWindow);
			}
		} catch (com.sun.star.lang.IllegalArgumentException ex) {
			ex.printStackTrace();
			throw new com.sun.star.lang.IllegalArgumentException(
					"Method external_event requires a string in the event object argument.", this, (short) -1);
		}
		return true;
	}

	private void saveData(XWindow aWindow)
			throws com.sun.star.lang.IllegalArgumentException, com.sun.star.uno.Exception {
		// Determine the name of the options page. This serves two purposes. First, if
		// this
		// options page is supported by this handler and second we use the name two
		// locate
		// the corresponding data in the registry.
		String sWindowName = DialogHelper.getWindowName(aWindow);
		if (sWindowName == null)
			throw new com.sun.star.lang.IllegalArgumentException("This window is not supported by this handler", this,
					(short) -1);

		// To access the separate controls of the window we need to obtain the
		// XControlContainer from the window implementation
		XControlContainer xContainer = (XControlContainer) UnoRuntime.queryInterface(XControlContainer.class, aWindow);
		if (xContainer == null)
			throw new com.sun.star.uno.Exception("Could not get XControlContainer from window.", this);

		// This is an implementation which will be used for several options pages
		// which all have the same controls. m_arStringControls is an array which
		// contains the names.
		for (int i = 0; i < m_controlNames.length; i++) {
			// To obtain the data from the controls we need to get their model.
			// First get the respective control from the XControlContainer.
			XControl[] s = xContainer.getControls();
			XControl xControl = xContainer.getControl(m_controlNames[i]);

			// This generic handler and the corresponding registry schema support
			// up to five text controls. However, if a options page does not use all
			// five controls then we will not complain here.
			if (xControl == null)
				continue;

			// From the control we get the model, which in turn supports the
			// XPropertySet interface, which we finally use to get the data from
			// the control.
			XPropertySet xProp = (XPropertySet) UnoRuntime.queryInterface(XPropertySet.class, xControl.getModel());

			if (xProp == null)
				throw new com.sun.star.uno.Exception("Could not get XPropertySet from control.", this);

			// Retrieve the data we want to store from the components.
			// We do not know which property contains data we want, so
			// we decide through the components name. This only works if all
			// components have been named properly:
			// Text fields start with "txt",
			// Check boxes with "chk",
			// List boxes with "lst"
			// You should adapt this behavior to your needs.
			Object aObj = null;
			Object[] value = new Object[1];
			String[] keys = new String[] { m_controlNames[i] };
			try {
				if (m_controlNames[i].startsWith("txt")) {
					aObj = xProp.getPropertyValue("Text");
					value[0] = AnyConverter.toString(aObj);
				}
			} catch (com.sun.star.lang.IllegalArgumentException ex) {
				ex.printStackTrace();
				throw new com.sun.star.lang.IllegalArgumentException("Wrong property type.", this, (short) -1);
			}

			// Now we have the actual string value of the control. What we need now is
			// the XPropertySet of the respective property in the registry, so that we
			// can store the value.
			// To access the registry we have previously created a service instance
			// of com.sun.star.configuration.ConfigurationUpdateAccess which supports
			// com.sun.star.container.XNameAccess. The XNameAccess is used to get the
			// particular registry node which represents this options page.
			// Fortunately the name of the window is the same as the registry node.
			System.out.println("Before saving");
			XPropertySet xLeaf = (XPropertySet) UnoRuntime.queryInterface(XPropertySet.class,
					accessLeaves.getByName(sWindowName));
			if (xLeaf == null)
				throw new com.sun.star.uno.Exception("XPropertySet not supported.", this);

			// Finally we can set the values
			for (int n = 0; n < keys.length; n++)
				xLeaf.setPropertyValue(keys[n], value[n]);
		}

		// Committing the changes will cause or changes to be written to the registry.
		XChangesBatch xUpdateCommit = (XChangesBatch) UnoRuntime.queryInterface(XChangesBatch.class, accessLeaves);
		xUpdateCommit.commitChanges();
	}

	private void loadData(XWindow aWindow) throws com.sun.star.uno.Exception {
		// Determine the name of the window. This serves two purposes. First, if this
		// window is supported by this handler and second we use the name two locate
		// the corresponding data in the registry.
		String sWindowName = DialogHelper.getWindowName(aWindow);
		if (sWindowName == null)
			throw new com.sun.star.lang.IllegalArgumentException("The window is not supported by this handler", this,
					(short) -1);

		// To acces the separate controls of the window we need to obtain the
		// XControlContainer from window implementation
		XControlContainer xContainer = (XControlContainer) UnoRuntime.queryInterface(XControlContainer.class, aWindow);
		if (xContainer == null)
			throw new com.sun.star.uno.Exception("Could not get XControlContainer from window.", this);

		// This is an implementation which will be used for several options pages
		// which all have the same controls. m_arStringControls is an array which
		// contains the names.
		for (int i = 0; i < m_controlNames.length; i++) {
			// load the values from the registry
			// To access the registry we have previously created a service instance
			// of com.sun.star.configuration.ConfigurationUpdateAccess which supports
			// com.sun.star.container.XNameAccess. We obtain now the section
			// of the registry which is assigned to this options page.
			XPropertySet xLeaf = (XPropertySet) UnoRuntime.queryInterface(XPropertySet.class,
					this.accessLeaves.getByName(sWindowName));
			if (xLeaf == null)
				throw new com.sun.star.uno.Exception("XPropertySet not supported.", this);

			// The properties in the registry have the same name as the respective
			// controls. We use the names now to obtain the property values.
			Object aValue = xLeaf.getPropertyValue(m_controlNames[i]);

			// Now that we have the value we need to set it at the corresponding
			// control in the window. The XControlContainer, which we obtained earlier
			// is the means to get hold of all the controls.
			XControl xControl = xContainer.getControl(m_controlNames[i]);

			// This generic handler and the corresponding registry schema support
			// up to five text controls. However, if a options page does not use all
			// five controls then we will not complain here.
			if (xControl == null)
				continue;

			// From the control we get the model, which in turn supports the
			// XPropertySet interface, which we finally use to set the data at the
			// control
			XPropertySet xProp = (XPropertySet) UnoRuntime.queryInterface(XPropertySet.class, xControl.getModel());

			if (xProp == null)
				throw new com.sun.star.uno.Exception("Could not get XPropertySet from control.", this);

			// Some default handlings: you can freely adapt the behaviour to your
			// needs, this is only an example.
			// For text controls we set the "Text" property.
			if (m_controlNames[i].startsWith("txt")) {
				xProp.setPropertyValue("Text", aValue);
			}
			// The available properties for a checkbox are defined in file
			// offapi/com/sun/star/awt/UnoControlCheckBoxModel.idl
			else if (m_controlNames[i].startsWith("chk")) {
				xProp.setPropertyValue("State", aValue);
			}
			// The available properties for a checkbox are defined in file
			// offapi/com/sun/star/awt/UnoControlListBoxModel.idl
			else if (m_controlNames[i].startsWith("lst")) {
				xProp.setPropertyValue("StringItemList", aValue);

				aValue = xLeaf.getPropertyValue(m_controlNames[i] + "Selected");
				xProp.setPropertyValue("SelectedItems", aValue);
			}
		}
	}

	@Override
	public String[] getSupportedMethodNames() {
		return new String[] { "external_event" };
	}

}
