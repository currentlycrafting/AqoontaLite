const { app, BrowserWindow, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const net = require('net'); // For checking port availability
const http = require('http'); // For making HTTP requests (health check)
const fs = require('fs'); // For file system operations (logging)

let flaskProcess = null;
let mainWindow;

const FLASK_PORT = 5000; // Flask app will run on this port
const FLASK_URL = `http://127.0.0.1:${FLASK_PORT}`;
const MAX_FLASK_STARTUP_ATTEMPTS = 30; // Increased from 10 (30 seconds total wait)
const FLASK_STARTUP_RETRY_DELAY = 1000; // Remains 1 second, but total wait time is longer

// Define log file path in user data directory
const logFilePath = path.join(app.getPath('userData'), 'flask_backend_log.txt');
// console.log removed: `Flask backend logs will be written to: ${logFilePath}`

// Function to write to log file
function writeToLog(message) {
    fs.appendFileSync(logFilePath, `${new Date().toISOString()} - ${message}\n`);
}

// Function to check if a port is in use
function isPortInUse(port) {
    return new Promise((resolve) => {
        const tester = net.createServer()
            .once('error', (err) => {
                if (err.code === 'EADDRINUSE') {
                    writeToLog(`Port ${port} is already in use.`);
                    resolve(true); // Port is in use
                } else {
                    writeToLog(`Error checking port ${port}: ${err.message}`);
                    resolve(false); // Other error, assume not in use or handle differently
                }
            })
            .once('listening', () => {
                writeToLog(`Port ${port} is free.`);
                tester.once('close', () => {
                    resolve(false); // Port is free
                }).close();
            })
            .listen(port);
    });
}

// Function to check if Flask server is ready
function checkFlaskServer(attempt = 1) {
    return new Promise((resolve, reject) => {
        if (attempt > MAX_FLASK_STARTUP_ATTEMPTS) {
            writeToLog(`Flask server did not respond after ${MAX_FLASK_STARTUP_ATTEMPTS} attempts.`);
            return reject(new Error(`Flask server did not respond after ${MAX_FLASK_STARTUP_ATTEMPTS} attempts.`));
        }

        writeToLog(`Attempting to connect to Flask server (${FLASK_URL}). Attempt ${attempt}/${MAX_FLASK_STARTUP_ATTEMPTS}...`);
        // console.log removed: `Attempting to connect to Flask server (${FLASK_URL}). Attempt ${attempt}/${MAX_FLASK_STARTUP_ATTEMPTS}...`

        const req = http.get(FLASK_URL, (res) => {
            if (res.statusCode === 200) {
                writeToLog('Flask server is ready!');
                // console.log removed: 'Flask server is ready!'
                resolve(true);
            } else {
                writeToLog(`Flask server responded with status ${res.statusCode}. Retrying...`);
                // console.warn removed: `Flask server responded with status ${res.statusCode}. Retrying...`
                setTimeout(() => checkFlaskServer(attempt + 1).then(resolve).catch(reject), FLASK_STARTUP_RETRY_DELAY);
            }
        });

        req.on('error', (err) => {
            writeToLog(`Flask server connection error: ${err.message}. Retrying...`);
            // console.warn removed: `Flask server connection error: ${err.message}. Retrying...`
            setTimeout(() => checkFlaskServer(attempt + 1).then(resolve).catch(reject), FLASK_STARTUP_RETRY_DELAY);
        });

        req.end();
    });
}

// Function to start the Flask backend
async function startFlaskBackend() {
    const portInUse = await isPortInUse(FLASK_PORT);
    if (portInUse) {
        console.error(`Port ${FLASK_PORT} is already in use. Cannot start Flask backend.`);
        dialog.showErrorBox('Application Error', `Port ${FLASK_PORT} is already in use. Please close any other applications using this port and restart Aqoonta Lite.`);
        app.quit();
        return;
    }

    let flaskExecutablePath;
    if (app.isPackaged) {
        flaskExecutablePath = path.join(process.resourcesPath, 'backend', 'dist', 'FlaskBackend');
    } else {
        flaskExecutablePath = path.join(__dirname, 'backend', 'dist', 'FlaskBackend');
    }

    writeToLog(`Attempting to spawn Flask backend from: ${flaskExecutablePath}`);
    // console.log removed: `Attempting to spawn Flask backend from: ${flaskExecutablePath}`

    try {
        const logStream = fs.createWriteStream(logFilePath, { flags: 'a' });
        flaskProcess = spawn(flaskExecutablePath, [], {
            stdio: ['ignore', logStream.fd, logStream.fd] // Redirect stdout and stderr to logStream's file descriptor
        });

        // These stdout/stderr listeners are primarily for development console debugging.
        // They will still write to the log file via stdio redirection.
        flaskProcess.stdout.on('data', (data) => {
            // console.log removed: `Flask stdout (also in log file): ${data}`
        });

        flaskProcess.stderr.on('data', (data) => {
            // console.error removed: `Flask stderr (also in log file): ${data}`
        });

        flaskProcess.on('close', (code) => {
            writeToLog(`Flask process exited with code ${code}`);
            console.log(`Flask process exited with code ${code}`); // Keep this for critical exit info
            flaskProcess = null;
            if (code !== 0) {
                dialog.showErrorBox('Application Error', `The Flask backend unexpectedly exited with code ${code}. Please restart the application.`);
                app.quit();
            }
        });

        flaskProcess.on('error', (err) => {
            writeToLog(`Failed to spawn Flask process: ${err}`);
            console.error(`Failed to spawn Flask process: ${err}`); // Keep this for critical errors
            dialog.showErrorBox('Application Error', `Failed to start the Flask backend: ${err.message}. Please ensure the backend executable is not corrupted and try again.`);
            app.quit();
        });

        // Wait for Flask server to be ready before proceeding
        await checkFlaskServer();
        writeToLog("Flask backend ready. Proceeding to create main window and load Flask URL.");
        // console.log removed: "Flask backend ready. Proceeding to create main window and load Flask URL."

    } catch (err) {
        writeToLog(`Error during Flask backend startup: ${err}`);
        console.error(`Error during Flask backend startup: ${err}`); // Keep this for critical errors
        dialog.showErrorBox('Application Error', `An error occurred during Flask backend startup: ${err.message}.`);
        app.quit();
    }
}

function createMainWindow() {
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
        },
        title: "Aqoonta Lite"
    });

    // Directly load the Flask URL into the main window
    writeToLog(`Loading Flask URL: ${FLASK_URL} into main window.`); // Keep this for log file
    // console.log removed: `Loading Flask URL: ${FLASK_URL} into main window.`
    mainWindow.loadURL(FLASK_URL);

    // Removed: mainWindow.webContents.openDevTools(); // No automatic DevTools in production
    mainWindow.on('closed', () => {
        writeToLog("Main window closed."); // Keep this for log file
        // console.log removed: "Main window closed."
        mainWindow = null;
    });
}

app.on('ready', async () => {
    // Clear the log file at the start of a new session
    if (fs.existsSync(logFilePath)) {
        fs.unlinkSync(logFilePath);
    }
    writeToLog("Electron app 'ready' event fired. Starting new session.");
    // console.log removed: "Electron app 'ready' event fired."

    // First, start the Flask backend and wait for it to be ready
    await startFlaskBackend();

    // Then, create the main window and load the Flask URL
    createMainWindow();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
    writeToLog("All windows closed. App quitting (if not macOS).");
    // console.log removed: "All windows closed. App quitting (if not macOS)."
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        writeToLog("App activated, no windows open. Creating new main window.");
        // console.log removed: "App activated, no windows open. Creating new main window."
        createMainWindow();
    }
});

app.on('will-quit', () => {
    if (flaskProcess) {
        writeToLog("Killing Flask backend process...");
        console.log("Killing Flask backend process..."); // Keep this for critical exit info
        flaskProcess.kill();
        flaskProcess = null;
    }
});
