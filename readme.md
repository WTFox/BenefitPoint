
# BenefitPoint

This project is a python wrapper to interface with BenefitPoint webservices. 

## Installation

Just download or clone this project then run
``` bash 

    python setup.py install

```

## Usage

The Sagitta class takes 2 parameters to initalize - Username and Password. In the example below logins.py looks something like this: 

``` python 

    # logins.py
    
    benefitpoint = dict(
        username='you@me.com',
        password='benefitpointpass'
    )


```

``` python

import logins
from benefitpoint import BenefitPoint

bp = BenefitPoint(**logins.benefitpoint)

# Create the complex type
productSearchCriteria = bp.create_type('ns1:ProductSearchCriteria')
productSearchCriteria.accountID = 1344234

# Call the method and send in the complex type, productSearchCriteria, as a param.
productSummaries = bp.call('findProducts', productSearchCriteria)

for product in productSummaries:
    print(product)

```

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## History

Nothing to see here yet folks

## License

MIT: [http://rem.mit-license.org](http://rem.mit-license.org)