# Chapter 29: Clean Embedded Architecture

## Core Idea
"Firmware" is not defined by where code lives (ROM vs. RAM) but by what it depends on — code tightly coupled to hardware/processor/OS details is firmware and has a short useful life, while a clean embedded architecture uses layered abstraction boundaries (HAL, PAL, OSAL) to keep the bulk of the code as long-lived, off-target-testable software.

## Frameworks Introduced
- **Software vs. firmware redefinition**: "Although software does not wear out, it can be destroyed from within by unmanaged dependencies on firmware and hardware" (Grenning's extension of Doug Schmidt's claim that "firmware and hardware become obsolete, thereby requiring software modifications"). Firmware is defined by *what it depends on*, not by storage medium.
  - When to use: Whenever classifying embedded (or any hardware/platform-adjacent) code as software vs. firmware.
  - How: Ask what the code depends on — if it depends on hardware/processor/OS specifics, it's firmware regardless of where it's stored; minimize the amount of code in this category.
- **Three-layer clean embedded architecture (Software / Firmware / Hardware)** with abstraction seams between each:
  - When to use: Structuring any embedded system to survive hardware/OS churn and enable off-target testing.
  - How: Insert a Hardware Abstraction Layer (HAL) between firmware and software; insert a Processor Abstraction Layer (PAL) to isolate processor/compiler-extension dependencies within firmware; insert an Operating System Abstraction Layer (OSAL) between software and the OS/RTOS.
- **App-titude test (Kent Beck's three activities, applied to embedded)**: "First make it work. Then make it right. Then make it fast." Passing only step 1 ("make it work") without step 2 ("make it right") is the App-titude test — necessary but insufficient for long-lived code.
  - When to use: As a self-check after any feature is functionally complete but before considering it done.
  - How: After the code works, refactor explicitly for understandability/evolvability (make it right) before micro-optimizing for performance (make it fast); don't skip straight from "works" to "fast."
- **DRY conditional compilation via HAL**: Replace repeated `#ifdef BOARD_V2`-style conditional compilation scattered throughout the codebase with a HAL that hides the hardware-type decision behind a single set of interfaces, resolved via linker or runtime binding instead of thousands of preprocessor branches.
  - When to use: When target-hardware conditional compilation directives are repeated across many files (the chapter cites one telecom app with thousands of `#ifdef BOARD_V2` occurrences).
  - How: Move the hardware-type decision under the HAL's interface; bind the correct implementation at link time or runtime rather than scattering `#ifdef` blocks through business logic.

## Key Concepts
- **Firmware (redefined)**: Code that is firmware "because of what it depends on and how hard it is to change as hardware evolves" — not because it's stored in ROM/EPROM/flash (the chapter explicitly rejects the standard dictionary definitions).
- **Target-hardware bottleneck**: The specific embedded failure mode where code can only be tested on the actual target hardware, because no abstraction seam exists to substitute a test double — this bottleneck slows development whenever hardware is unavailable, buggy, or scarce.
- **Hardware Abstraction Layer (HAL)**: The boundary between software and firmware; its API is shaped by what the software needs (e.g., name/value persistence, `Indicate_LowBattery()`), not by what the hardware exposes (e.g., raw flash writes, GPIO bit `Led_TurnOn(5)`) — hardware detail must never leak through it.
- **Processor Abstraction Layer (PAL)**: A layer isolating firmware from compiler-vendor C-language extensions (custom keywords, direct register-mapped "variables") so that only a small, confined part of firmware is bound to the silicon/toolchain.
- **Operating System Abstraction Layer (OSAL)**: The boundary isolating software from the OS/RTOS API and semantics, so that switching RTOS vendors means writing a new OSAL implementation (to a known interface) rather than modifying scattered application code.
- **Programming to interfaces / substitutability**: The general principle (header files as interface definitions, limited to function declarations and only the constants/structs the interface needs) that makes every layer's boundary a genuine test/substitution seam.
- **stdint.h vs. vendor headers (e.g., acmetypes.h)**: A concrete portability pattern — write a local `stdint.h` that depends on the vendor header only for target builds, so the rest of the codebase depends on the portable standard type names instead of vendor-specific types.

## Mental Models
- Think of "firmware" as a dependency classification, not a storage location — any code (embedded or not) that buries SQL, platform APIs, or OS calls directly in business logic is "writing firmware," even on a desktop or Android app.
- Use "can this code be tested off the target hardware?" as the litmus test for a clean embedded architecture — a successful HAL/PAL/OSAL is defined by the substitution seam it provides for off-target testing, not by its abstraction elegance.
- Think of layering as fractal, not fixed: a HAL can itself expose higher-level product-meaningful services (`Indicate_LowBattery()`) built on lower-level hardware primitives (`Led_TurnOn(5)`) — layers can contain layers.
- Treat vendor-supplied "helpful" headers and C-language extensions with suspicion: convenience today ties the codebase to one compiler/processor tomorrow; confine such usage to as few files as possible.

## Anti-patterns
- **Legacy code as the spec**: In the TDM-to-VOIP migration example, the tangled legacy system had no separation between hardware/protocol details and business logic — the only way to answer a "how should this behave" question was to read undocumented, hardware-entangled code, because the whole product had effectively become firmware.
- **Message processor polluted with UART details**: A message dispatcher that could have had a long useful life as pure software instead lives in the same file as UART hardware interaction code, permanently coupling protocol logic to a specific hardware peripheral.
- **Stopping at "make it work" (App-titude test only)**: Shipping code organized by whatever order functions were written in (ISRs, button handlers, domain logic, and flash storage all interleaved in one file) rather than refactoring for structure — functional but with no chance at a long useful life, and testable only on-target.
- **Using vendor extension headers directly in business code**: Including `acmetypes.h`-style vendor type headers (or raw register-mapped globals like `IE`, `SBUF0`, `TI_0`) outside of a narrowly confined firmware/PAL layer ties the whole codebase to one microcontroller family and prevents off-target testing.
- **Thousands of repeated `#ifdef` directives**: Using conditional compilation (e.g., `#ifdef BOARD_V2`) thousands of times across a codebase to select hardware variants violates DRY and should instead be resolved once, behind a HAL interface.

## Code Examples
```c
#ifndef _ACME_STD_TYPES
#define _ACME_STD_TYPES
#if defined(_ACME_X42)
typedef unsigned int  Uint_32;
typedef unsigned short Uint_16;
typedef unsigned char Uint_8;
typedef int   Int_32;
typedef short Int_16;
typedef char  Int_8;
#elif defined(_ACME_A42)
typedef unsigned long Uint_32;
typedef unsigned int  Uint_16;
typedef unsigned char Uint_8;
typedef long Int_32;
typedef int  Int_16;
typedef char Int_8;
#else
#error <acmetypes.h> is not supported for this environment
#endif
#endif
```
```c
#ifndef _STDINT_H_
#define _STDINT_H_
#include <acmetypes.h>
typedef Uint_32 uint32_t;
typedef Uint_16 uint16_t;
typedef Uint_8  uint8_t;
typedef Int_32  int32_t;
typedef Int_16  int16_t;
typedef Int_8   int8_t;
#endif
```
- **What it demonstrates**: Instead of letting application code depend directly on vendor-specific `acmetypes.h`, a locally-written `stdint.h` wraps it — the rest of the codebase depends only on the portable standard type names (`uint32_t`, etc.), confining the vendor dependency to one file and enabling portability/off-target builds.

```c
void say_hi() {
    IE = 0b11000000;
    SBUF0 = (0x68); while(TI_0 == 0); TI_0 = 0;
    SBUF0 = (0x69); while(TI_0 == 0); TI_0 = 0;
    SBUF0 = (0x0a); while(TI_0 == 0); TI_0 = 0;
    SBUF0 = (0x0d); while(TI_0 == 0); TI_0 = 0;
    IE = 0b11010000;
}
```
- **What it demonstrates**: Real-world firmware directly manipulating compiler-extension "variables" (`IE`, `SBUF0`, `TI_0`) that map to micro-controller peripheral registers — convenient but not standard C; a clean embedded architecture confines this kind of code to very few places (behind a PAL) so the rest of the firmware stays portable and off-target testable.

## Reference Tables
| Layer boundary | Isolates software from... | Named abstraction |
|---|---|---|
| Software / Firmware | Hardware implementation details (storage medium, GPIO assignments) | HAL (Hardware Abstraction Layer) |
| Firmware / Processor | Compiler vendor extensions, register-mapped pseudo-variables | PAL (Processor Abstraction Layer) |
| Software / OS or RTOS | OS-specific APIs and concurrency primitives | OSAL (Operating System Abstraction Layer) |

## Worked Example
A small embedded system's source file mixes 16 functions with no organization: ISRs (`TIMER1_vect`, `INT2_vect`), a button handler, domain logic (`calc_RPM`, `Do_Average`, `Get_Next_Measurement`, `Zero_Sensor_1/2`), raw hardware access (`Read_RawData`), persistent storage (`Load_FLASH_Setup`, `Save_FLASH_Setup`, `Store_DataSet`, `bytes2float`, `Recall_DataSet`), and a misleadingly-named `Sensor_init`. Grenning regroups them by actual concern: domain logic, hardware platform setup, button-press reaction, raw A/D input, and persistent storage — revealing that the single file conflates at least four distinct architectural responsibilities with no boundaries between them, and that every function assumes it's running on the specific microprocessor architecture, using extended C constructs tied to one toolchain. The code "works" (passes the App-titude test) but cannot be tested off-target and cannot survive a hardware change without a full rewrite — the diagnostic example for why a HAL (separating hardware-setup functions), a PAL (confining the extended-C register access), and clean grouping of domain logic from persistence are all needed.

## Key Takeaways
1. Classify code as firmware vs. software by its dependencies, not its storage location — minimize the amount of true firmware in any system, embedded or not.
2. Use the App-titude test as a warning, not a finish line: "it works" (Kent Beck's step 1) is necessary but must be followed by "make it right" before the code can have a long useful life.
3. Insert a HAL shaped by the software's needs (not the hardware's raw capabilities) as the seam between firmware and software — this is what makes off-target testing possible.
4. Confine processor/compiler-vendor extensions (custom keywords, register-mapped globals) to a narrow PAL, and confine OS/RTOS-specific calls to a narrow OSAL, so switching either later means writing new code to a known interface rather than modifying scattered call sites.
5. Treat header files strictly as interface definitions (function declarations plus only the constants/structs actually needed) — don't leak implementation-only details into shared headers, or the "interface" becomes another coupling vector.
6. Replace repeated `#ifdef HARDWARE_VARIANT` conditional compilation with a HAL interface resolved at link/runtime — thousands of scattered `#ifdef`s is a DRY violation, not an inherent embedded requirement.
7. Recognize that non-embedded developers write "firmware" too, whenever they bury SQL or platform-specific API calls directly inside business logic — the chapter's lesson generalizes beyond embedded systems.

## Connects To
- **Ch 25 (Layers and Boundaries)**: HAL/PAL/OSAL are concrete, embedded-specific instances of the general layering and boundary-drawing principles from Ch 25.
- **Ch 28 (The Test Boundary)**: The target-hardware bottleneck is embedded's version of the Fragile Tests Problem — both are solved by inserting substitution seams (Testing API vs. HAL/OSAL) that enable testing without the volatile dependency.
- **Dependency Rule / Dependency Inversion**: HAL, PAL, and OSAL are all applications of dependency inversion — software defines the interface it needs, and firmware/OS/processor-specific code implements it, keeping the dependency arrow pointed toward the more stable, abstract software layer.
