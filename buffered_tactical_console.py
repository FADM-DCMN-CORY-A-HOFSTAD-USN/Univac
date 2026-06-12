# File Name: buffered_tactical_console.py
# Location: Root source folder
# Subsystem: Memory-Buffered Low-Latency Tactical Direct-Fire Console

import tkinter as tk
import math
import time
import threading

class BufferedTacticalConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("UNIVAC BACKUP CONSOLE - ZERO-LAG MEMORY BUFFER TYPE")
        self.root.geometry("1100x650")
        self.root.configure(bg="#0c0c0c")

        # BUFFER 1: HIGH-SPEED TELEMETRY AND FIRING MATRIX (THREAD-ISOLATED)
        # This dictionary is updated instantly by raw hardware inputs.
        # It handles firing calculations completely independently of the visual graphics.
        self.firing_data_lock = threading.Lock()
        self.high_speed_numeric_buffer = {
            'target_bearing_deg': 45.0,
            'target_distance_px': 150.0,
            'current_azimuth_deg': 0.0,
            'current_elevation_deg': 0.0,
            'is_target_locked': False,
            'trigger_dispatched': False,
            'last_calc_timestamp': time.time()
        }
    # Insert this calculation step inside your high-speed hardware math thread loop:
    with self.firing_data_lock:
    # Read live navigation bus variables from the network router
    v_vessel = live_telemetry.get('speed_ms', 0.0)
    yaw_rate = live_telemetry.get('yaw_rate_rads', 0.0)
    roll_angle = live_telemetry.get('roll_angle_rad', 0.0)
    
    # 1. Apply forward velocity vector lead compensation
    tgt_bearing_rad = math.radians(self.high_speed_numeric_buffer['target_bearing_deg'])
    muzzle_velocity = 825.0 # Standard 5-inch shell speed (m/s)
    
    lead_correction_rad = math.asin((v_vessel * math.sin(tgt_bearing_rad)) / muzzle_velocity)
    
    # 2. Adjust target calculations based on hull-relative movements
    compensated_bearing = self.high_speed_numeric_buffer['target_bearing_deg'] + math.degrees(lead_correction_rad)
    
    # 3. Apply the helm turn rate prediction offset over the shell's estimated 4-second time-of-flight
    time_of_flight = 4.0
    predicted_slew_offset = math.degrees(yaw_rate * time_of_flight)
    
    self.high_speed_numeric_buffer['current_azimuth_deg'] = compensated_bearing - predicted_slew_offset

        # BUFFER 2: GRAPHICS IMAGE BUFFER MEMORY
        # Fixed 400x400 canvas footprint mapping raw pixel states
        self.img_w = 400
        self.img_h = 400
        
        # Instantiate a clean, low-overhead Tkinter memory photo map
        # This serves as our visual back-buffer to eliminate GPU bottlenecks
        self.memory_image_buffer = tk.PhotoImage(width=self.img_w, height=self.img_h)

        self._build_interface_layout()
        
        # Launch the high-speed tracking math loop on an independent thread
        self.math_loop_active = True
        self.math_thread = threading.Thread(target=self._hardware_math_execution_worker, daemon=True)
        self.math_thread.start()

        # Start the low-priority UI frame swap tick loop
        self._start_visual_blit_tick()

    def _build_interface_layout(self):
        """Builds a high-contrast console layout."""
        # Top Banner Warning Strip
        banner = tk.Frame(self.root, bg="#210505", height=40, bd=1, relief=tk.SOLID)
        banner.pack(fill=tk.X, side=tk.TOP)
        
        lbl_alert = tk.Label(banner, text="DUAL-BUFFER SEPARATION MODE: TARGETING PLANT BYPASSES DISPLAY QUEUES", 
                             bg="#210505", fg="#ff3333", font=('Courier', 11, 'bold'))
        lbl_alert.pack(side=tk.LEFT, padx=15, pady=8)

        # Main Workspace Container
        panel_container = tk.Frame(self.root, bg="#0c0c0c")
        panel_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Column: Image Buffer Display Frame
        left_column = tk.Frame(panel_container, bg="#0c0c0c")
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Visual label mapping directly to our pre-built memory image block
        self.blit_display_screen = tk.Label(left_column, image=self.memory_image_buffer, bg="#000000", bd=2, relief=tk.RIDGE)
        self.blit_display_screen.pack(padx=10, pady=10)

        # Right Column: Diagnostic Reporting Box
        right_column = tk.Frame(panel_container, bg="#141414", width=450, bd=1, relief=tk.SOLID)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

        lbl_ops = tk.Label(right_column, text="[ CO-PROCESSOR REAL-TIME TELEMETRY ]", bg="#141414", fg="#00ff00", font=('Courier', 11, 'bold'))
        lbl_ops.pack(anchor=tk.W, padx=15, pady=10)

        self.telemetry_box = tk.Text(right_column, width=48, height=15, bg="#000000", fg="#00ff00", font=('Courier', 10))
        self.telemetry_box.pack(padx=15, pady=5)

        # Manual Trigger Controls
        control_deck = tk.Frame(right_column, bg="#141414")
        control_deck.pack(fill=tk.X, padx=15, pady=20)

        btn_slew = tk.Button(control_deck, text="ENGAGE RE-TRACKING", bg="#1c1c1c", fg="#00ff00", font=('Courier', 10, 'bold'), command=self._manually_shift_mock_target)
        btn_slew.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        btn_fire = tk.Button(control_deck, text="FORCE DIRECT ENGAGEMENT", bg="#590000", fg="#ffffff", activebackground="#ff0000", font=('Courier', 10, 'bold'), command=self._execute_instant_engagement)
        btn_fire.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)

    def _hardware_math_execution_worker(self):
        """
        BUFFER 1 WORKER: Runs inside a dedicated thread context.
        Executes raw tracking calculations without waiting for graphic redraw frames.
        """
        print("[PLANT] High-speed numeric firing buffer thread active.")
        loop_interval = 0.01  # Run tracking at a fast 100Hz cadence
        
        while self.math_loop_active:
            start_loop = time.time()
            
            with self.firing_data_lock:
                # 1. Update mock cross-axis track movements over time
                self.high_speed_numeric_buffer['target_bearing_deg'] = (self.high_speed_numeric_buffer['target_bearing_deg'] + 0.3) % 360.0
                
                # 2. Direct-Fire Control Law: Calculate mechanical turret tracking lag
                t_bearing = self.high_speed_numeric_buffer['target_bearing_deg']
                c_azimuth = self.high_speed_numeric_buffer['current_azimuth_deg']
                
                error_az = t_bearing - c_azimuth
                # Handle tracking ring roll-over boundaries smoothly
                error_az = (error_az + 180.0) % 360.0 - 180.0
                
                # Execute rapid servo movement prediction
                self.high_speed_numeric_buffer['current_azimuth_deg'] += error_az * 0.25
                
                # 3. Automation Interlock Check: If alignment error is minimal, verify lock state
                if abs(error_az) < 0.5:
                    self.high_speed_numeric_buffer['is_target_locked'] = True
                else:
                    self.high_speed_numeric_buffer['is_target_locked'] = False
                    self.high_speed_numeric_buffer['trigger_dispatched'] = False
                    
                self.high_speed_numeric_buffer['last_calc_timestamp'] = start_loop

            # Enforce hard deterministic clock interval pacing
            elapsed = time.time() - start_loop
            sleep_time = loop_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _render_image_buffer_pixels(self):
        """
        BUFFER 2 RENDERER: Builds a flat string array in memory 
        and updates the visual photo map using a direct block-transfer (BLIT).
        """
        cx, cy = self.img_w // 2, self.img_h // 2
        
        # Grab a safe snapshot of current positions to construct the image frame
        with self.firing_data_lock:
            azimuth_snapshot = self.high_speed_numeric_buffer['current_azimuth_deg']
            target_bearing_snapshot = self.high_speed_numeric_buffer['target_bearing_deg']
            target_dist_snapshot = self.high_speed_numeric_buffer['target_distance_px']
            locked_state = self.high_speed_numeric_buffer['is_target_locked']

        # Determine geometric pixel placement for tracking line
        rad_az = math.radians(azimuth_snapshot)
        end_x = int(cx + (cx - 20) * math.sin(rad_az))
        end_y = int(cy - (cy - 20) * math.cos(rad_az))
        
        # Determine geometric pixel placement for target point
        rad_tgt = math.radians(target_bearing_snapshot)
        tgt_x = int(cx + target_dist_snapshot * math.sin(rad_tgt))
        tgt_y = int(cy - target_dist_snapshot * math.cos(rad_tgt))

        # --- COMPUTE BLOCK PIXEL MATRIX TRANSFORMS ---
        mount_color = "#00ff00" if not locked_state else "#ffcc00"
        tgt_color = "#00ff00" if not locked_state else "#ff0000"

        # Clear memory image canvas back-buffer to flat dark green
        self.memory_image_buffer.blank()

        # Blit reticle components via block-transfer logic
        try:
            # Render target reticle box directly onto pixel memory coordinates
            self.memory_image_buffer.put(tgt_color, to=(tgt_x-4, tgt_y-4, tgt_x+4, tgt_y+4))
            
            # Render a cross-hair cursor pattern centered on the tactical origin
            self.memory_image_buffer.put("#003300", to=(cx-50, cy, cx+50, cy+1))
            self.memory_image_buffer.put("#003300", to=(cx, cy-50, cx, cy+50))
            
            # Draw tracking pointer position line coordinates
            self.memory_image_buffer.put(mount_color, to=(end_x-2, end_y-2, end_x+2, end_y+2))
        except Exception:
            pass # Handle transient calculation overflow gracefully

    def _manually_shift_mock_target(self):
        """Forces target vector coordinates to step instantly to break tracking lock."""
        with self.firing_data_lock:
            self.high_speed_numeric_buffer['target_bearing_deg'] = (self.high_speed_numeric_buffer['target_bearing_deg'] + 120.0) % 360.0
            self.high_speed_numeric_buffer['trigger_dispatched'] = False

    def _execute_instant_engagement(self):
        """Direct-fire manual trigger overrule intercepting high-speed memory variables."""
        with self.firing_data_lock:
            if self.high_speed_numeric_buffer['is_target_locked']:
                self.high_speed_numeric_buffer['trigger_dispatched'] = True
                print(f"[ENGAGEMENT] DIRECT FIRE DISPATCHED ON RAW MEMORY METRICS (AZ: {self.high_speed_numeric_buffer['current_azimuth_deg']:.2f}°)")

    def _start_visual_blit_tick(self):
        """Low-priority visual update loop running at a standard, flicker-free 20Hz."""
        # 1. Execute back-buffer pixel conversions and blit to screen
        self._render_image_buffer_pixels()
        
        # 2. Extract telemetry strings to populate diagnostics text windows
        with self.firing_data_lock:
            snap = self.high_speed_numeric_buffer.copy()
            
        self.telemetry_box.delete("1.0", tk.END)
# Cleaned separator layout prevents rendering engine breaks
report = (
"=== HIGH-SPEED HARDWARE REGISTER PROFILE ===\n" +
f"NUMERIC CALCULATION TIMESTEP: {snap['last_calc_timestamp']:.4f}\n" +
f"TARGET REJECTION DIRECTION: {snap['target_bearing_deg']:8.2f}°\n" +
f"MOUNT BEARING POSITION: {snap['current_azimuth_deg']:8.2f}°\n" +
f"TRACKING SYSTEM ERROR RATIO: {abs(snap['target_bearing_deg'] - snap['current_azimuth_deg']):8.4f}°\n" +
"============================================\n" +
f"HARDWARE TARGET LOCK STATUS: {'[ LOCKED ]' if snap['is_target_locked'] else '[ SEARCHING ]'}\n" +
f"AUTOMATED DIRECT FIRE DISPATCH: {'[ ACTIVE FIRING ]' if snap['trigger_dispatched'] else '[ HOLD ]'}\n" +
"============================================\n" +
"STATUS: Visual rendering separated cleanly\n" +
"from underlying numeric calculation tracking matrices."
)
self.telemetry_box.insert(tk.END, report)
# Continuous visual recurrence cycle (Every 50ms)
self.root.after(50, self._start_visual_blit_tick)
Core Entry Initializer
if name == "main":
ui_frame = tk.Tk()
app = BufferedTacticalConsole(ui_frame)
ui_frame.mainloop()

