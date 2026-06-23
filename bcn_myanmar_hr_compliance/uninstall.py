import click

from bcn_myanmar_hr_compliance.setup import before_uninstall as cleanup


def after_install():
	try:
		print("Removing customizations created by BCN Myanmar HR Compliance...")
		cleanup()

	except Exception as e:
		click.secho(
			"Removing Customizations for BCN Myanmar HR Compliance app failed due to an error."
			" Please try re-installing the app.",
			fg="bright_red",
		)
		raise e

	click.secho("BCN Myanmar HR Compliance app customizations have been removed successfully...", fg="green")
