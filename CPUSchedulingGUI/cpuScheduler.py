import tkinter as tk
from tkinter import ttk

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        
        # Input Frame
        self.input_frame = ttk.LabelFrame(root, text="Input", padding=(10, 10))
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(self.input_frame, text="Processes (comma-separated):").grid(row=0, column=0, sticky="w")
        self.process_entry = ttk.Entry(self.input_frame, width=30)
        self.process_entry.grid(row=0, column=1, pady=5)

        ttk.Label(self.input_frame, text="Burst Times (comma-separated):").grid(row=1, column=0, sticky="w")
        self.burst_entry = ttk.Entry(self.input_frame, width=30)
        self.burst_entry.grid(row=1, column=1, pady=5)

        ttk.Label(self.input_frame, text="Priorities (comma-separated, for Priority-based):").grid(row=2, column=0, sticky="w")
        self.priority_entry = ttk.Entry(self.input_frame, width=30)
        self.priority_entry.grid(row=2, column=1, pady=5)

        ttk.Label(self.input_frame, text="Algorithm:").grid(row=3, column=0, sticky="w")
        self.algorithm_var = tk.StringVar(value="FCFS")
        self.algorithm_menu = ttk.Combobox(self.input_frame, textvariable=self.algorithm_var, values=["FCFS", "SJF", "Priority", "NPP", "SRTF", "PP", "Round Robin"])
        self.algorithm_menu.grid(row=3, column=1, pady=5)

        ttk.Label(self.input_frame, text="Time Quantum (for Round Robin):").grid(row=4, column=0, sticky="w")
        self.time_quantum_entry = ttk.Entry(self.input_frame, width=10)
        self.time_quantum_entry.grid(row=4, column=1, sticky="w")

        self.simulate_button = ttk.Button(self.input_frame, text="Simulate", command=self.simulate)
        self.simulate_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Output Frame
        self.output_frame = ttk.LabelFrame(root, text="Output", padding=(10, 10))
        self.output_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(self.output_frame, text="Timeline:").grid(row=0, column=0, sticky="w")
        self.timeline_canvas = tk.Canvas(self.output_frame, height=80, bg="white")
        self.timeline_canvas.grid(row=1, column=0, pady=5, sticky="ew")

        ttk.Label(self.output_frame, text="Gantt Chart:").grid(row=2, column=0, sticky="w")
        self.gantt_canvas = tk.Canvas(self.output_frame, height=80, bg="white")
        self.gantt_canvas.grid(row=3, column=0, pady=5, sticky="ew")

        self.output_frame.columnconfigure(0, weight=1)

    def simulate(self):
        processes = self.process_entry.get().split(',')
        burst_times = list(map(int, self.burst_entry.get().split(',')))
        priorities = list(map(int, self.priority_entry.get().split(','))) if self.priority_entry.get() else None
        algorithm = self.algorithm_var.get()

        if algorithm == "FCFS":
            timeline, gantt_chart = self.fcfs(processes, burst_times)
        elif algorithm == "SJF":
            timeline, gantt_chart = self.sjf(processes, burst_times)
        elif algorithm == "Round Robin":
            time_quantum = int(self.time_quantum_entry.get())
            timeline, gantt_chart = self.round_robin(processes, burst_times, time_quantum)
        elif algorithm == "NPP":
            timeline, gantt_chart = self.npp(processes, burst_times, priorities)
        elif algorithm == "SRTF":
            timeline, gantt_chart = self.srtf(processes, burst_times)
        elif algorithm == "PP":
            timeline, gantt_chart = self.pp(processes, burst_times, priorities)
        else:
            timeline, gantt_chart = [], []

        self.display_timeline(timeline)
        self.display_gantt_chart(gantt_chart)

    def fcfs(self, processes, burst_times):
        timeline = []
        gantt_chart = []
        current_time = 0

        for process, burst in zip(processes, burst_times):
            timeline.append((process, current_time, current_time + burst))
            gantt_chart.append((process, current_time, current_time + burst))
            current_time += burst

        return timeline, gantt_chart

    def sjf(self, processes, burst_times):
        timeline = []
        gantt_chart = []
        current_time = 0

        sorted_processes = sorted(zip(processes, burst_times), key=lambda x: x[1])
        for process, burst in sorted_processes:
            timeline.append((process, current_time, current_time + burst))
            gantt_chart.append((process, current_time, current_time + burst))
            current_time += burst

        return timeline, gantt_chart

    def npp(self, processes, burst_times, priorities):
        timeline = []
        gantt_chart = []
        current_time = 0

        sorted_processes = sorted(zip(processes, burst_times, priorities), key=lambda x: x[2])
        for process, burst, _ in sorted_processes:
            timeline.append((process, current_time, current_time + burst))
            gantt_chart.append((process, current_time, current_time + burst))
            current_time += burst

        return timeline, gantt_chart

    def srtf(self, processes, burst_times):
        timeline = []
        gantt_chart = []
        remaining_times = burst_times[:]
        current_time = 0

        while any(remaining_times):
            available = [(i, burst) for i, burst in enumerate(remaining_times) if burst > 0]
            if available:
                i, burst = min(available, key=lambda x: x[1])
                timeline.append((processes[i], current_time, current_time + 1))
                gantt_chart.append((processes[i], current_time, current_time + 1))
                remaining_times[i] -= 1
                current_time += 1

        return timeline, gantt_chart

    def pp(self, processes, burst_times, priorities):
        timeline = []
        gantt_chart = []
        remaining_times = burst_times[:]
        current_time = 0

        while any(remaining_times):
            available = [(i, pri) for i, (burst, pri) in enumerate(zip(remaining_times, priorities)) if burst > 0]
            if available:
                i, _ = min(available, key=lambda x: x[1])
                timeline.append((processes[i], current_time, current_time + 1))
                gantt_chart.append((processes[i], current_time, current_time + 1))
                remaining_times[i] -= 1
                current_time += 1

        return timeline, gantt_chart

    def round_robin(self, processes, burst_times, time_quantum):
        timeline = []
        gantt_chart = []
        current_time = 0
        remaining_times = burst_times[:]
        queue = list(range(len(processes)))

        while queue:
            process_idx = queue.pop(0)
            process = processes[process_idx]
            burst = remaining_times[process_idx]

            if burst > time_quantum:
                timeline.append((process, current_time, current_time + time_quantum))
                gantt_chart.append((process, current_time, current_time + time_quantum))
                current_time += time_quantum
                remaining_times[process_idx] -= time_quantum
                queue.append(process_idx)
            else:
                timeline.append((process, current_time, current_time + burst))
                gantt_chart.append((process, current_time, current_time + burst))
                current_time += burst

        return timeline, gantt_chart

    def display_timeline(self, timeline):
        self.timeline_canvas.delete("all")
        width = self.timeline_canvas.winfo_width()
        height = self.timeline_canvas.winfo_height()

        # Draw the main horizontal line with arrows on both ends
        self.timeline_canvas.create_line(20, height // 2, width - 20, height // 2, arrow="both", width=2)

        x_start = 20  # Starting point for the timeline
        scale = (width - 40) / (max(end for _, _, end in timeline))  # Scale based on max end time

        for process, start, end in timeline:
            # Calculate positions for the start and end points
            start_x = x_start + start * scale
            end_x = x_start + end * scale

            # Draw tick marks for the start and end points
            self.timeline_canvas.create_line(start_x, height // 2 - 10, start_x, height // 2 + 10, width=1)
            self.timeline_canvas.create_line(end_x, height // 2 - 10, end_x, height // 2 + 10, width=1)

            # Add the process name at the end tick
            self.timeline_canvas.create_text(end_x, height // 2 - 20, text=f"{process}", anchor="center", font=("Arial", 10))

            # Add time labels below the start and end tick marks
            self.timeline_canvas.create_text(start_x, height // 2 + 20, text=f"{start}", anchor="n", font=("Arial", 8))
            self.timeline_canvas.create_text(end_x, height // 2 + 20, text=f"{end}", anchor="n", font=("Arial", 8))


        


    def display_gantt_chart(self, gantt_chart):
        self.gantt_canvas.delete("all")

        # Get the canvas dimensions
        canvas_width = self.gantt_canvas.winfo_width() - 20  # Account for padding
        canvas_height = self.gantt_canvas.winfo_height()

        # Determine the total duration (end of the last process)
        max_time = max(end for _, _, end in gantt_chart)

        # Calculate scaling factor to fit within canvas width
        scale = canvas_width / max_time if max_time > 0 else 1

        x = 10  # Initial x position (left padding)
        for process, start, end in gantt_chart:
            # Scale the width dynamically
            box_width = (end - start) * scale

            # Draw the rectangle for the process
            self.gantt_canvas.create_rectangle(x, 10, x + box_width, 40, fill="skyblue", outline="black")

            # Draw the process name inside the box
            self.gantt_canvas.create_text(x + box_width / 2, 25, text=f"{process}", anchor="center")

            # Draw the start time below the left edge of the rectangle
            self.gantt_canvas.create_text(x, 50, text=f"{start}", anchor="n")

            # Draw the end time below the right edge of the rectangle
            self.gantt_canvas.create_text(x + box_width, 50, text=f"{end}", anchor="n")

            # Move the x position to the right for the next box
            x += box_width



if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()