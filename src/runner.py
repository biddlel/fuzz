import subprocess
import sys

import mutators
import process

class Manager:

    _MUTATORS = {
        "csv" : mutators.CSV_Mutator,
        "json" : mutators.JSON_Mutator
    }
    
    def __init__(self, binary, seed, times: int = 5000):
        self._num_runs = times
        self._current_checkpoint = 0
        
        if "./"  != binary[1:2]:
            self._process_name = f"./{binary}"
        else:
            self._process_name = f"{binary}"
        
        self._stop_flag = False
        
        try:
            self._inputFile = open(seed, 'r')
            self._inputStr = self.inputFile.read().strip()

        except OSError:
            print(f"Couldn't open input file: {self.inputFile}")
            sys.exit()


        self._file_type = process.whichType(self.inputStr)
        self._fuzz = self.MUTATORS[self.type](self._inputStr)

    def _init_process(self):
        self._process = subprocess.Popen(
            self._binary_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def _reset(self):
        self._init_process()

    def _log_result(self, idx: int, name: str, input_bytes: bytes, outs: bytes, err: bytes, exitcode: int):
        """Print and log the result of the processing."""
        status = 'PASSED' if exitcode >= 0 else 'CRASHED'
        print(f"{idx+1} {status} | exitcode: {exitcode}")
        print(f"\t{'method:':<12}{name}")
        print(f"\t{'input_length:':<12}{len(input_bytes)}")
        print("=" * 50)

    def _result_dump(self, input):
        with open(f"{self._txt_name}_dump.txt", "w+") as fp:
            fp.write(input)
            fp.close()
    
    def run(self):
        self._txt_name = self._process_name.split('/')[-1].split('.')[0]
        for idx, (input_bytes, name) in enumerate(self._fuzzer, 1):
            if idx > self._num_runs:
                break
            try:
                outs, err, exitcode = self._process_input(input_bytes)
                self._log_result(idx, name, input_bytes, outs, err, exitcode)

                if exitcode < 0:  # Handle SIGFAULT
                    print(f"Program Crashed: exitcode = {exitcode}")
                    print(f"\tReason: {process.ExitCodes.name[-exitcode]}")
                    print(f"Dumped badinput to {self._txt_name}_dump.txt")
                    self._result_dump(input_bytes)
            except subprocess.TimeoutExpired:
                print(f"{idx}: Timeout")
                print(f"Dumped timeout report to {self._txt_name}_dump.txt")
                self._result_dump(input_bytes)
            
            self._reset()
        

    



    
        
        