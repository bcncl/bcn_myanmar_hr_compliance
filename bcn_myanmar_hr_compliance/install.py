import click

from bcn_myanmar_hr_compliance.setup import after_install as setup


def after_install():
	try:
		print("Setting up HR Complinance for Myanmar Region...")
		setup()
		click.secho("Thank you for installing BCN Myanmar HR Compliance!", fg="green")

	except Exception as e:
		click.secho(
			"Installation for BCN Myanmar HR Compliance app failed due to an error."
			" Please try re-installing the app.",
			fg="bright_red",
		)
		raise e
