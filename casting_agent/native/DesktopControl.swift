import AppKit
import ApplicationServices
import Foundation

// Native local control only. No extension, cookies, browser debugging, or model API.
let chromeBundle = "com.google.Chrome"
let allowedHosts: Set<String> = ["bon-kercasting.ca", "www.bon-kercasting.ca", "facebook.com", "www.facebook.com", "mail.google.com"]
let navigationLabels: Set<String> = ["My Profile", "Photos & Documents", "Open Jobs", "Discussion", "See more"]
let arguments = Array(CommandLine.arguments.dropFirst())

func emit(_ value: [String: Any], code: Int32 = 0) -> Never {
    let data = try! JSONSerialization.data(withJSONObject: value, options: [.sortedKeys])
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write(Data([10]))
    exit(code)
}

func fail(_ code: String, _ message: String) -> Never {
    emit(["ok": false, "error": ["code": code, "message": message]], code: 2)
}

func permittedURL(_ raw: String) -> URL {
    guard let parts = URLComponents(string: raw),
          parts.scheme == "https",
          let host = parts.host, allowedHosts.contains(host.lowercased()),
          parts.port == nil || parts.port == 443,
          parts.user == nil, parts.password == nil,
          let url = parts.url else {
        fail("url_not_allowed", "Choose an HTTPS Bon-Ker, Facebook, or Gmail page.")
    }
    return url
}

func attribute(_ element: AXUIElement, _ name: String) -> CFTypeRef? {
    var result: CFTypeRef?
    return AXUIElementCopyAttributeValue(element, name as CFString, &result) == .success ? result : nil
}

func stringAttribute(_ element: AXUIElement, _ name: String) -> String {
    if let value = attribute(element, name) as? String { return value }
    if let value = attribute(element, name) as? URL { return value.absoluteString }
    return ""
}

func children(_ element: AXUIElement) -> [AXUIElement] {
    attribute(element, "AXChildren") as? [AXUIElement] ?? []
}

func chrome() -> NSRunningApplication {
    guard let app = NSRunningApplication.runningApplications(withBundleIdentifier: chromeBundle).first else {
        fail("chrome_not_running", "Open Chrome at a permitted casting page first.")
    }
    return app
}

func focusedWindow(_ app: NSRunningApplication) -> AXUIElement {
    let application = AXUIElementCreateApplication(app.processIdentifier)
    guard let value = attribute(application, "AXFocusedWindow"),
          CFGetTypeID(value) == AXUIElementGetTypeID() else {
        fail("window_unavailable", "Chrome has no accessible focused window.")
    }
    return unsafeBitCast(value, to: AXUIElement.self)
}

func requireAccessibility() {
    guard AXIsProcessTrusted() else {
        fail("accessibility_required", "macOS Accessibility access is required. No permission was requested or changed.")
    }
}

func findWebArea(_ window: AXUIElement) -> AXUIElement {
    var queue: [AXUIElement] = [window]
    var index = 0
    while index < queue.count && index < 1500 {
        let element = queue[index]
        index += 1
        if stringAttribute(element, "AXRole") == "AXWebArea" { return element }
        queue.append(contentsOf: children(element))
    }
    fail("page_unavailable", "Chrome did not expose an accessible web page. No page data was substituted.")
}

func pageURL(_ area: AXUIElement) -> String {
    let raw = stringAttribute(area, "AXURL")
    guard !raw.isEmpty else { fail("page_url_unavailable", "Cannot verify the selected page URL.") }
    return permittedURL(raw).absoluteString
}

func label(_ element: AXUIElement) -> String {
    for name in ["AXTitle", "AXDescription"] {
        let value = stringAttribute(element, name)
        if !value.isEmpty { return value }
    }
    if stringAttribute(element, "AXRole") == "AXStaticText" {
        return stringAttribute(element, "AXValue")
    }
    return ""
}

func pointAttribute(_ element: AXUIElement) -> CGPoint? {
    guard let value = attribute(element, "AXPosition"), CFGetTypeID(value) == AXValueGetTypeID() else { return nil }
    var point = CGPoint.zero
    return AXValueGetValue(unsafeBitCast(value, to: AXValue.self), .cgPoint, &point) ? point : nil
}

func sizeAttribute(_ element: AXUIElement) -> CGSize? {
    guard let value = attribute(element, "AXSize"), CFGetTypeID(value) == AXValueGetTypeID() else { return nil }
    var size = CGSize.zero
    return AXValueGetValue(unsafeBitCast(value, to: AXValue.self), .cgSize, &size) ? size : nil
}

func frame(_ element: AXUIElement) -> CGRect? {
    guard let point = pointAttribute(element), let size = sizeAttribute(element) else { return nil }
    return CGRect(origin: point, size: size)
}

func snapshot() -> [String: Any] {
    requireAccessibility()
    let app = chrome()
    let window = focusedWindow(app)
    let area = findWebArea(window)
    let url = pageURL(area) // Validate origin before collecting text.
    var records: [[String: Any]] = []
    var visited = Set<CFHashCode>()
    var characterCount = 0
    var truncated = false
    var processed = 0
    func walk(_ element: AXUIElement, _ path: [Int], _ depth: Int) {
        if processed >= 2000 || depth > 50 || characterCount >= 50000 { truncated = true; return }
        let hash = CFHash(element)
        if visited.contains(hash) { return }
        visited.insert(hash)
        processed += 1
        if stringAttribute(element, "AXSubrole") == "AXSecureTextField" { return }
        let role = stringAttribute(element, "AXRole")
        let text = String(label(element).prefix(2000))
        if !text.isEmpty {
            var record: [String: Any] = ["role": role, "text": text, "path": path]
            if let bounds = frame(element), bounds.width > 0, bounds.height > 0 {
                record["bounds"] = ["x": bounds.minX, "y": bounds.minY, "width": bounds.width, "height": bounds.height]
            }
            records.append(record)
            characterCount += text.count
        }
        for (index, child) in children(element).enumerated() { walk(child, path + [index], depth + 1) }
    }
    walk(area, [], 0)
    guard !records.isEmpty else { fail("empty_page", "The page exposed no readable content.") }
    return [
        "ok": true, "source": "macos_accessibility", "url": url,
        "window_title": stringAttribute(window, "AXTitle"),
        "observed_at": ISO8601DateFormatter().string(from: Date()),
        "truncated": truncated, "nodes": records
    ]
}

func pump(_ seconds: TimeInterval) {
    RunLoop.current.run(until: Date(timeIntervalSinceNow: seconds))
}

func clickNavigation(_ expectedURL: String, _ expectedLabel: String) -> Never {
    requireAccessibility()
    guard navigationLabels.contains(expectedLabel) else {
        fail("action_not_allowed", "This prototype only clicks approved navigation labels.")
    }
    _ = permittedURL(expectedURL)
    let app = chrome()
    let window = focusedWindow(app)
    let area = findWebArea(window)
    guard pageURL(area) == expectedURL else { fail("page_changed", "The active page changed. Read it again before clicking.") }
    var matches: [AXUIElement] = []
    var queue = [area]
    var index = 0
    while index < queue.count && index < 2000 {
        let element = queue[index]
        index += 1
        let role = stringAttribute(element, "AXRole")
        if ["AXButton", "AXLink", "AXTab"].contains(role) && label(element) == expectedLabel {
            matches.append(element)
        }
        queue.append(contentsOf: children(element))
    }
    guard matches.count == 1, let target = matches.first,
          let targetFrame = frame(target), let windowFrame = frame(window),
          targetFrame.width > 0, targetFrame.height > 0 else {
        fail("target_not_unique", "No single visible navigation control matched. No click was sent.")
    }
    let point = CGPoint(x: targetFrame.midX, y: targetFrame.midY)
    guard windowFrame.contains(point) else { fail("target_not_visible", "Scroll the control into view first.") }
    // Avoid clicking an overlapping application. The user must select Chrome first.
    guard NSWorkspace.shared.frontmostApplication?.processIdentifier == app.processIdentifier else {
        fail("chrome_not_frontmost", "Select Chrome before sending a mouse click.")
    }
    guard let down = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left),
          let up = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left) else {
        fail("event_unavailable", "Could not create the mouse event.")
    }
    down.post(tap: .cghidEventTap)
    up.post(tap: .cghidEventTap)
    emit(["ok": true, "action": "mouse_click", "sent": true, "verified_result": false, "label": expectedLabel])
}

final class PrototypeWindow: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    let urlField = NSTextField(string: "https://bon-kercasting.ca/my-profile")
    let output = NSTextView()
    var observedURL: String?

    func applicationDidFinishLaunching(_ notification: Notification) {
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 820, height: 640),
                          styleMask: [.titled, .closable, .miniaturizable, .resizable],
                          backing: .buffered, defer: false)
        window.title = "Casting Partner — Desktop Proof"
        window.center()
        let stack = NSStackView()
        stack.orientation = .vertical
        stack.alignment = .leading
        stack.spacing = 14
        stack.translatesAutoresizingMaskIntoConstraints = false
        window.contentView!.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: window.contentView!.leadingAnchor, constant: 22),
            stack.trailingAnchor.constraint(equalTo: window.contentView!.trailingAnchor, constant: -22),
            stack.topAnchor.constraint(equalTo: window.contentView!.topAnchor, constant: 22),
            stack.bottomAnchor.constraint(equalTo: window.contentView!.bottomAnchor, constant: -22)
        ])
        let explanation = NSTextField(wrappingLabelWithString:
            "Real Chrome page reader. Data stays in this window. No extension, AI service, or submissions. Accessibility access must be granted by you in macOS.")
        explanation.font = .systemFont(ofSize: 17)
        stack.addArrangedSubview(explanation)
        urlField.font = .systemFont(ofSize: 18)
        urlField.setAccessibilityLabel("Casting page URL")
        urlField.heightAnchor.constraint(greaterThanOrEqualToConstant: 40).isActive = true
        stack.addArrangedSubview(urlField)
        let row = NSStackView()
        row.orientation = .horizontal
        row.spacing = 10
        for (title, selector) in [
            ("Check Access", #selector(checkAccess)),
            ("Open Chrome Page", #selector(openPage)),
            ("Read Chrome Page", #selector(readPage))
        ] {
            let button = NSButton(title: title, target: self, action: selector)
            button.font = .systemFont(ofSize: 16)
            button.heightAnchor.constraint(greaterThanOrEqualToConstant: 46).isActive = true
            row.addArrangedSubview(button)
        }
        stack.addArrangedSubview(row)
        let secondRow = NSStackView()
        secondRow.orientation = .horizontal
        secondRow.spacing = 10
        for (title, selector) in [
            ("Open Accessibility Settings", #selector(openSettings)),
            ("Open Jobs with Mouse", #selector(openJobs))
        ] {
            let button = NSButton(title: title, target: self, action: selector)
            button.font = .systemFont(ofSize: 16)
            button.heightAnchor.constraint(greaterThanOrEqualToConstant: 46).isActive = true
            secondRow.addArrangedSubview(button)
        }
        stack.addArrangedSubview(secondRow)
        let scroll = NSScrollView()
        scroll.hasVerticalScroller = true
        scroll.borderType = .bezelBorder
        output.isEditable = false
        output.isSelectable = true
        output.isVerticallyResizable = true
        output.autoresizingMask = [.width]
        output.frame = NSRect(x: 0, y: 0, width: 760, height: 320)
        output.textContainer?.widthTracksTextView = true
        output.font = .monospacedSystemFont(ofSize: 14, weight: .regular)
        output.setAccessibilityLabel("Live result or permission error")
        scroll.documentView = output
        stack.addArrangedSubview(scroll)
        scroll.heightAnchor.constraint(greaterThanOrEqualToConstant: 300).isActive = true
        scroll.widthAnchor.constraint(equalTo: stack.widthAnchor).isActive = true
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        output.string = "Choose Check Access. No permissions are requested automatically."
    }

    func runCommand(_ args: [String]) {
        output.string = "Checking…"
        DispatchQueue.global().async {
            let process = Process()
            process.executableURL = Bundle.main.executableURL
            process.arguments = args
            let pipe = Pipe()
            process.standardOutput = pipe
            process.standardError = FileHandle.nullDevice
            var text = ""
            do {
                try process.run()
                let data = pipe.fileHandleForReading.readDataToEndOfFile()
                process.waitUntilExit()
                text = String(data: data, encoding: .utf8) ?? "Invalid helper response."
            } catch {
                text = "The native helper could not run."
            }
            let resultText = text
            DispatchQueue.main.async {
                self.output.string = resultText
                if let data = resultText.data(using: .utf8),
                   let result = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                   result["source"] as? String == "macos_accessibility" {
                    self.observedURL = result["url"] as? String
                }
            }
        }
    }

    @objc func checkAccess() { runCommand(["status"]) }
    @objc func openPage() { observedURL = nil; runCommand(["open", urlField.stringValue]) }
    @objc func readPage() { runCommand(["read"]) }
    @objc func openSettings() {
        // Opens the settings page only. This never changes a privacy toggle.
        NSWorkspace.shared.open(URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility")!)
    }
    @objc func openJobs() {
        guard let url = observedURL else {
            output.string = "Read the casting page first so the navigation target can be verified."
            return
        }
        NSRunningApplication.runningApplications(withBundleIdentifier: chromeBundle).first?.activate(options: [])
        runCommand(["click", url, "Open Jobs"])
    }
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }
}

func showPrototype() -> Never {
    let application = NSApplication.shared
    application.setActivationPolicy(.regular)
    let delegate = PrototypeWindow()
    application.delegate = delegate
    withExtendedLifetime(delegate) { application.run() }
    exit(0)
}

switch arguments.first ?? (Bundle.main.bundleURL.pathExtension == "app" ? "app" : "status") {
case "app":
    showPrototype()
case "status":
    emit([
        "ok": true, "platform": "macos", "accessibility": AXIsProcessTrusted(),
        "chrome_running": !NSRunningApplication.runningApplications(withBundleIdentifier: chromeBundle).isEmpty,
        "permissions_requested": false
    ])
case "open":
    guard arguments.count == 2 else { fail("invalid_arguments", "open requires a URL.") }
    let url = permittedURL(arguments[1])
    let installedURL = URL(fileURLWithPath: "/Applications/Google Chrome.app")
    guard let applicationURL = NSWorkspace.shared.urlForApplication(withBundleIdentifier: chromeBundle)
        ?? (FileManager.default.fileExists(atPath: installedURL.path) ? installedURL : nil) else {
        fail("chrome_missing", "Google Chrome is not installed.")
    }
    let configuration = NSWorkspace.OpenConfiguration()
    configuration.activates = true
    var completed = false
    var succeeded = false
    var launchError: NSError?
    NSWorkspace.shared.open([url], withApplicationAt: applicationURL, configuration: configuration) { app, error in
        succeeded = app != nil && error == nil
        launchError = error as NSError?
        completed = true
    }
    let deadline = Date(timeIntervalSinceNow: 15)
    while !completed && Date() < deadline { pump(0.05) }
    guard succeeded else {
        let detail = launchError.map { " (\($0.domain) \($0.code))" } ?? ""
        fail("open_failed", "macOS could not open the URL in Chrome" + detail + ".")
    }
    emit(["ok": true, "action": "open_url", "url": url.absoluteString, "page_read": false])
case "read":
    emit(snapshot())
case "click":
    guard arguments.count == 3 else { fail("invalid_arguments", "click requires the last observed URL and a navigation label.") }
    clickNavigation(arguments[1], arguments[2])
default:
    fail("invalid_command", "Use status, open, read, or click.")
}
