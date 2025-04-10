import csv
import itertools
import sys

PROBS = {
    # Unconditional probabilities for having gene
    "gene": {2: 0.01, 1: 0.03, 0: 0.96},
    "trait": {
        # Probability of trait given two copies of gene
        2: {True: 0.65, False: 0.35},
        # Probability of trait given one copy of gene
        1: {True: 0.56, False: 0.44},
        # Probability of trait given no gene
        0: {True: 0.01, False: 0.99},
    },
    # Mutation probability
    "mutation": 0.01,
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])
    # people = load_data(
    #     "D:\\Python_repositories\\Harvard_CS50_AI\\2_uncertainty\\Data\\Heredity\\family0.csv"
    # )

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {"gene": {2: 0, 1: 0, 0: 0}, "trait": {True: 0, False: 0}}
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):
        # Check if current set of people violates known information
        fails_evidence = any(
            (
                people[person]["trait"] is not None
                and people[person]["trait"] != (person in have_trait)
            )
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (
                    True
                    if row["trait"] == "1"
                    else False
                    if row["trait"] == "0"
                    else None
                ),
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s)
        for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def parent_prob(parent: str, one_gene: set, two_genes: set) -> float:
    if parent in two_genes:
        return 1 - PROBS["mutation"]
    elif parent in one_gene:
        return 0.5  # 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]
    else:
        return PROBS["mutation"]


def joint_probability(
    people: dict, one_gene: set, two_genes: set, have_trait: set
) -> float:
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    probability = 1

    for person in people:
        personsMother = people[person]["mother"]
        personsFather = people[person]["father"]

        if person in two_genes:
            num_genes = 2
        elif person in one_gene:
            num_genes = 1
        else:
            num_genes = 0

        if personsMother is None and personsFather is None:
            gene_prob = PROBS["gene"][num_genes]
        else:
            from_mom_prob = parent_prob(personsMother, one_gene, two_genes)
            from_dad_prob = parent_prob(personsFather, one_gene, two_genes)

            if num_genes == 2:
                gene_prob = from_mom_prob * from_dad_prob
            elif num_genes == 1:
                gene_prob = from_mom_prob * (1 - from_dad_prob) + from_dad_prob * (
                    1 - from_mom_prob
                )
            else:
                gene_prob = (1 - from_mom_prob) * (1 - from_dad_prob)

        trait_prob = PROBS["trait"][num_genes][person in have_trait]

        probability *= gene_prob * trait_prob
    return probability


def update(
    probabilities: dict, one_gene: set, two_genes: set, have_trait: set, p: dict
) -> None:
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        num_genes = 2 if person in two_genes else 1 if person in one_gene else 0
        probabilities[person]["gene"][num_genes] += p
        probabilities[person]["trait"][person in have_trait] += p


def normalize(probabilities: dict) -> None:
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        for category in ["gene", "trait"]:
            total = sum(probabilities[person][category].values())
            for key in probabilities[person][category]:
                probabilities[person][category][key] /= total


if __name__ == "__main__":
    main()
