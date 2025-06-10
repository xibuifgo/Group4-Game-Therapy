import styles from './TSU.module.scss';

export default function TSignUp() {
    return(
        <div className={styles.Container}>
            <div className={styles.Box}>
                <h1>Sign Up</h1>
                <input type='email' id='email' placeholder='Enter Email' />
                <input type='text' id='username' placeholder='Enter Username' />
                <input type="password" id="password1" placeholder="Enter Password" />
                <input type="password" id="password2" placeholder="Repeat Password" />
                <button type='submit' className={styles.Btn}><p>Sign Up</p></button>
            </div>
        </div>
    );
}