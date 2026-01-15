# Nomadsky Digital Sovereignty

# Process Design


                   .--------------------------.
                  /                          /|
                 '         Nomadsky         / |
                +--------------------------+  |
                |           engine         |  +
                |                          | /
                '--------------------------'  
                  ^                    |
                  |                    |
                  |1) Download image   | 1) upload image
                  |                    |
                  |                    V
            .---------.             .---------.
          /          /|            /          /|
         '    VM 1  / |           '    VM 2  / |
        +----------+  |          +----------+  |
        |          |  +          |          |  +
        |          | /           |          | /
        '----------'             '----------'


### Step 1: Download image.
The code for this step is in folder named "Download images", and it depends on the vendor you are migrating from. 

### Step 2: upload image.
The code for this step is in folder named "upload images", and it depends on the vendor you are migrating to.

### Nomadsky engine
The code for the nomadsky engine is based on different features, which could be run like independent modules. 
1) Ground level code execution
2) transformation between VHD  or VMDK OS-format.


### Code development
The code follows a microservice architecture. So when developing new features, make the code in a way it can run independently. 
Use this template for creating new code



~~~
===============================================================================
FUNCTION TEMPLATE — AI & VIBE CODER FRIENDLY
===============================================================================

WHAT THIS FUNCTION DOES
-----------------------
Paste your prompt or Describe in 2–4 sentences:
- The business or technical goal of the function
- What problem it solves
- What it does NOT do (important for AI context)

Example:
Create a function processes input data, applies a transformation,
and returns a validated result. It does not perform I/O,
network calls, or persistence unless explicitly stated.

PARAMETERS (INPUT)
------------------
- param_a (type): Description of the parameter and constraints. it should contain a string like "sfsf-sfdsf-sdfsdf-eeer--2-22"
- param_b (type): Description, allowed values, optional/default behavior
- param_c (type, optional): Description

EXPECTED OUTPUT
---------------
- return_value (type): What the function returns and its meaning

LOGGING POLICY
--------------
- Use logging.debug() for internal state
- Use logging.info() for high-level milestones
- Use logging.warning() for recoverable issues
- Do NOT log sensitive data
===============================================================================

import logging
from typing import Any, Optional
logger = logging.getLogger(__name__)

def example_function(
    param_a: Any,
    param_b: int,
    param_c: Optional[str] = None,
) -> Any:
    """
    Short summary (1 line):
    Perform <action> on <input> and return <output>.

    Detailed explanation (optional):
    - Why this function exists
    - How it is typically used
    - Important assumptions
    """

    # -------------------------------------------------------------------------
    # PARAMETER VALIDATION (FAIL FAST)
    # -------------------------------------------------------------------------
    if param_a is None:
        raise ValueError("param_a must not be None")

    if not isinstance(param_b, int):
        raise TypeError("param_b must be of type int")

    if param_b <= 0:
        raise ValueError("param_b must be greater than zero")

    if param_c is not None and not isinstance(param_c, str):
        raise TypeError("param_c must be a string if provided")

    logger.debug(
        "Input parameters validated",
        extra={
            "param_b": param_b,
            "param_c_present": param_c is not None,
        },
    )

    # -------------------------------------------------------------------------
    # CORE LOGIC
    # -------------------------------------------------------------------------
    try:
        # TODO: Replace with actual logic
        # Keep logic deterministic and side-effect free where possible
        result = param_a  # placeholder transformation

        if param_c:
            # Example conditional behavior
            result = f"{result}-{param_c}"

    except Exception as exc:
        logger.exception("Unexpected error during core logic execution")
        raise RuntimeError("Function execution failed") from exc

    # -------------------------------------------------------------------------
    # OUTPUT VALIDATION
    # -------------------------------------------------------------------------
    if result is None:
        raise RuntimeError("Function returned None — this is not allowed")

    # Optional: strict type or shape check
    # if not isinstance(result, ExpectedType):
    #     raise TypeError("Output is not of expected type")

    logger.debug("Output validated successfully")

    # -------------------------------------------------------------------------
    # RETURN
    # -------------------------------------------------------------------------
    return result








