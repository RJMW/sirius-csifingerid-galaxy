import argparse
import os
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input')
parser.add_argument('--db_online')
parser.add_argument('--profile')
parser.add_argument('--candidates')
parser.add_argument('--ppm_max')
parser.add_argument('--polarity')
parser.add_argument('--results')
parser.add_argument('--out_dir')

args = parser.parse_args()
print args

with open(args.input,"r") as infile:
    first_read = True
    numlines = 0
    for line in infile:
        line = line.strip()
        if numlines == 0: #read the headers
            if "NAME" in line:
                featid = line.split("NAME: ")[1]
            if "PRECURSORMZ" in line:
                mz = float(line.split("PRECURSORMZ: ")[1])
                if args.polarity=="pos":
                    mz2 = mz-1.007276
                else:
                    mz2 = mz+1.007276
            if "Num Peaks" in line:
                numlines = int(line.split("Num Peaks: ")[1]) # number of spectra peaks
                linesread = 0
                peaklist = []
        else:
            if linesread != numlines: # read spectra
                line = tuple(line.split("\t"))
                linesread += 1
                peaklist.append(line)
            else:
                numlines = 0 #reset for next header
                #write spec file
                specpth = os.path.join(args.out_dir,'tmpspec.txt')
                tmpdir = os.path.join(args.out_dir,'tempout')
                with open(specpth, 'w') as outfile:
                    for p in peaklist:
                        outfile.write(p[0]+" "+p[1]+"\n")
                #create commandline input
                if args.polarity == "pos":
                    ion = "[M+H]+"
                else:
                    ion = "[M-H]-"
                cmd_command = "sirius "
                cmd_command += "-c {} -o {} -i {} -z {} -2 {} ".format(args.candidates, tmpdir , ion, mz, specpth)
                cmd_command += "-d {} --ppm-max {} --fingerid".format(args.db_online, args.ppm_max)
                # run
                print cmd_command
                os.system(cmd_command)
                # if fingerid found hits
                if os.path.exists(os.path.join(tmpdir, "1_tmpspec_", "summary_csi_fingerid.csv")):
                    with open(args.results, 'a') as outfile:
                        with open(os.path.join(tmpdir, "1_tmpspec_", "summary_csi_fingerid.csv")) as infile:
                            for line in infile:
                                if "inchi" in line:
                                    if first_read:
                                        line = line.replace("inchi","InChI")
                                        line = line.replace("rank", "Rank")
                                        line = line.replace("name", "Name")
                                        line = line.replace("score", "Score")
                                        outfile.write("UID\t"+line)
                                        first_read=False
                                else:
                                    outfile.write(featid+"\t"+ line)

